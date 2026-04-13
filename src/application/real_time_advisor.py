import json
import os
import webbrowser
from datetime import datetime

import pandas as pd
import structlog
import yfinance as yf

from src.application.audit_service import DeepAuditService
from src.application.backtest_service import ShadowBacktestService
from src.application.coordinator import StrategyOrchestrator
from src.application.learning import ProgressiveLearningService
from src.application.risk_manager import RiskManager
from src.application.services import ResearchIngestionService, TickerDiscoveryService, WikiMaintenanceService
from src.domain.portfolio import Portfolio
from src.domain.telemetry import LearningSummary, MLModelMetrics
from src.infrastructure.fs import FileSystemWikiAdapter
from src.infrastructure.llm import OllamaLLMAdapter
from src.infrastructure.predictive import QuantSignalProcessor, TrajectoryPredictor
from src.infrastructure.reporting import ReportGeneratorAdapter
from src.infrastructure.scraper import PoliteWebScraperAdapter

logger = structlog.get_logger()


class RealTimeAdvisor:
    """
    Orchestrates 'Today's Review' with Progressive Learning, ML, and Risk Management.
    """

    def __init__(self):
        self.llm = OllamaLLMAdapter()
        self.storage = FileSystemWikiAdapter()
        self.scraper = PoliteWebScraperAdapter()
        self.ingestion = ResearchIngestionService(self.scraper, self.storage)
        self.maintenance = WikiMaintenanceService(self.storage, self.llm)
        self.discovery = TickerDiscoveryService(self.storage, self.llm)
        self.orch = StrategyOrchestrator(self.llm, self.storage)
        self.report_gen = ReportGeneratorAdapter()
        self.learning = ProgressiveLearningService(self.storage, self.llm)
        self.predictor = TrajectoryPredictor()
        self.quant = QuantSignalProcessor()
        self.risk_mgr = RiskManager()
        self.audit = DeepAuditService(self.storage, self.llm)
        self.backtest = ShadowBacktestService()

    def get_fresh_price(self, symbol: str) -> float:
        try:
            ticker = yf.Ticker(symbol)
            return float(ticker.fast_info.get("last_price", ticker.history(period="1d")["Close"].iloc[-1]))
        except Exception:
            return 100.0

    def exercise_recommendations(
        self, recommendations: list[dict], portfolio: Portfolio, optimal_reserve: float
    ) -> None:
        print("\n--- 🛠️ EXERCISE RECOMMENDATIONS ---")

        do_now = []
        for i, rec in enumerate(recommendations):
            if rec.get("timing") != "IMMEDIATE":
                continue

            choice = input(
                f"[{i+1}] {rec['action']} {rec['symbol']} ({rec.get('company_name', 'N/A')})? [Y/n/defer]: "
            ).lower()
            if choice in ["", "y", "yes"]:
                do_now.append(rec)
            else:
                print(f"Skipping {rec['symbol']}...")

        if not do_now:
            print("No trades selected for execution.")
            return

        print("Fetching fresh execution prices...")
        current_total_val = portfolio.get_value({})
        for r in do_now:
            fresh_p = self.get_fresh_price(r["symbol"])
            r["price"] = fresh_p
            current_total_val += (r["quantity"] * fresh_p) if r["action"] == "BUY" else 0

        risk_floor = current_total_val * optimal_reserve
        deployable_cash = portfolio.cash - risk_floor

        if deployable_cash < 0:
            print(
                f"⚠️ Risk Protection Warning: Current cash (${portfolio.cash:.2f}) is below the ${risk_floor:.2f} safety floor."
            )
            deployable_cash = 0.0

        total_proposed_cost = sum(r["quantity"] * r["price"] for r in do_now if r["action"] in ["BUY", "SHORT"])

        if total_proposed_cost > deployable_cash:
            scale_factor = deployable_cash / total_proposed_cost if total_proposed_cost > 0 else 0.0
            for r in do_now:
                if r["action"] in ["BUY", "SHORT"]:
                    r["quantity"] *= scale_factor

        print("\n--- FINAL TRADE LIST (FRESH PRICES) ---")
        final_total = 0.0
        for r in do_now:
            cost = r["quantity"] * r["price"]
            final_total += cost
            print(f"- {r['action']} {r['quantity']:.4f} {r['symbol']} @ ${r['price']:.2f} | Est: ${cost:.2f}")

        print(f"\nTOTAL DEPLOYMENT: ${final_total:.2f}")
        print(f"POST-TRADE CASH:  ${(portfolio.cash - final_total):.2f}")
        print(f"RISK FLOOR:       ${risk_floor:.2f} ({optimal_reserve*100:.1f}%)")

        confirm = input("\nCommit these trades? [y/N]: ").lower()
        if confirm == "y":
            for r in do_now:
                if r["action"] == "BUY":
                    portfolio.buy(r["symbol"], r["quantity"], r["price"], r["rationale"])
                elif r["action"] == "SHORT":
                    portfolio.short(r["symbol"], r["quantity"], r["price"], r["rationale"])

            portfolio_path = os.path.join("src/infrastructure/data/portfolios", "fintrdr_portfolio_core.json")
            os.makedirs(os.path.dirname(portfolio_path), exist_ok=True)
            with open(portfolio_path, "w", encoding="utf-8") as f:
                f.write(portfolio.model_dump_json(indent=4))
            print("✅ Portfolio Updated.")
        else:
            print("Trades cancelled.")

    def run_morning_review(self) -> None:
        logger.info("Starting Morning Review with Risk Management", date=datetime.now().strftime("%Y-%m-%d"))

        portfolio_path = os.path.join("src/infrastructure/data/portfolios", "fintrdr_portfolio_core.json")
        if os.path.exists(portfolio_path):
            with open(portfolio_path) as f:
                current_portfolio = Portfolio.model_validate_json(f.read())
        else:
            current_portfolio = Portfolio(name="fintrdr-core-portfolio", cash=100.0)

        initial_balance = 100.0
        self.learning.audit_performance()
        self.scraper.fetch_headlines()
        self.maintenance.run_karpathy_loop()

        universe_path = "src/infrastructure/data/universe/ticker_universe.json"
        if os.path.exists(universe_path):
            with open(universe_path) as f:
                universe = json.load(f)
        else:
            universe = self.discovery.discover_tickers_from_wiki()

        if not universe:
            universe = ["AAPL", "NVDA", "GOOGL"]

        trajectories = {}
        quant_signals = {}
        current_prices = {}
        company_names = {}
        ml_results = []

        start_ml_time = datetime.now()
        if universe:
            try:
                hist_data = yf.download(universe, period="1mo")["Close"]
                for ticker in universe:
                    if not hist_data.empty:
                        if isinstance(hist_data, pd.Series):
                            prices = hist_data.dropna().tolist()
                        else:
                            prices = hist_data[ticker].dropna().tolist() if ticker in hist_data.columns else []

                        if prices:
                            current_prices[ticker] = prices[-1]
                            details = self.predictor.predict_trend_details(prices)
                            trajectories[ticker] = f"{details['trend']} (Slope: {details['slope']:.2f})"

                            # Simons Quant Signals
                            z_score = self.quant.calculate_z_score(prices)
                            regime = self.quant.detect_regime(prices)
                            quant_signals[ticker] = {"z": z_score, "regime": regime}

                            ml_results.append(details)
                    company_names[ticker] = ticker
            except Exception as e:
                logger.error("Failed to fetch real-time prices", error=str(e))

        # Fallback
        for ticker in universe:
            if ticker not in current_prices:
                current_prices[ticker] = 100.0
                trajectories[ticker] = "STABLE (Mock)"
                company_names[ticker] = ticker

        real_val = current_portfolio.get_value(current_prices)
        gain_loss_abs = real_val - initial_balance
        gain_loss_pct = (gain_loss_abs / initial_balance) * 100

        # Learning Metrics Summary
        if ml_results:
            avg_slope = sum(d["slope"] for d in ml_results) / len(ml_results)
            avg_r2 = sum(d["r2"] for d in ml_results) / len(ml_results)
            ml_metrics = MLModelMetrics(
                total_samples_analyzed=len(ml_results),
                mean_slope=avg_slope,
                volatility_index=1.0 - avg_r2,
                prediction_confidence_score=avg_r2,
                last_update_duration_ms=(datetime.now() - start_ml_time).total_seconds() * 1000,
            )
            sorted_tickers = sorted(trajectories.items(), key=lambda x: x[1], reverse=True)
            summary = LearningSummary(
                ml_metrics=ml_metrics,
                top_momentum_tickers=[t[0] for t in sorted_tickers[:5]],
                bottom_momentum_tickers=[t[0] for t in sorted_tickers[-5:]],
                system_evolution_notes="Simons-style quant signals integrated.",
            )
            summary_path = os.path.join("docs/reports", f"learning_summary_{datetime.now().strftime('%Y%m%d')}.json")
            with open(summary_path, "w") as sf:
                sf.write(summary.model_dump_json(indent=4))

        optimal_reserve = self.risk_mgr.determine_cash_reserve(trajectories)

        # Formulate Strategy
        strat = self.orch.formulate_strategy(
            persona_path=".github/agents/strategy-agent.agent.md",
            context_topic=f"Simons-Aware Pivot. Reserve: {optimal_reserve*100}%. Trajectories: {trajectories}. Quant Signals: {quant_signals}",
            active_universe=universe,
        )

        raw_immediate = []
        contingent_recommendations = []
        if strat:
            for rule in strat.rules:
                symbol = rule.params.get("symbol", "INDEX")
                price = current_prices.get(symbol, 100.0)
                timing = getattr(rule, "timing", "IMMEDIATE").upper()
                condition = rule.condition.lower()
                contingent_keywords = ["if", "breaks", "below", "above", "hits", "when", "target", "stops"]
                if any(k in condition for k in contingent_keywords) and condition != "first_day":
                    timing = "CONTINGENT"
                elif condition == "first_day":
                    timing = "IMMEDIATE"

                desired_val = current_portfolio.cash * 0.15
                desired_qty = desired_val / price if price > 0 else 0.0
                assessment = self.risk_mgr.validate_trade(
                    current_portfolio, symbol, quantity=desired_qty, price=price, cash_reserve_pct=optimal_reserve
                )

                rec = {
                    "symbol": symbol,
                    "company_name": company_names.get(symbol, symbol),
                    "action": rule.action,
                    "condition": rule.condition,
                    "quantity": assessment.recommended_quantity if assessment.is_approved else 0.0,
                    "price": price,
                    "timing": timing,
                    "rationale": f"Z-Score: {quant_signals.get(symbol, {}).get('z', 0.0):.2f}. Regime: {quant_signals.get(symbol, {}).get('regime', 'UNKNOWN')}. {strat.description}",
                    "agent": "Risk-Aware Strategy Agent",
                }
                if timing == "IMMEDIATE" and assessment.is_approved and rec["quantity"] > 0:
                    raw_immediate.append(rec)
                else:
                    contingent_recommendations.append(rec)

        final_recommendations = []
        risk_floor = real_val * optimal_reserve
        deployable_cash = max(0.0, current_portfolio.cash - risk_floor)

        if raw_immediate:
            total_cost = sum(r["quantity"] * r["price"] for r in raw_immediate if r["action"] in ["BUY", "SHORT"])
            scale_factor = 1.0
            if total_cost > deployable_cash and total_cost > 0:
                scale_factor = deployable_cash / total_cost
            for r in raw_immediate:
                if r["action"] in ["BUY", "SHORT"]:
                    r["quantity"] *= scale_factor
                final_recommendations.append(r)

        final_recommendations.extend(contingent_recommendations)

        # Intelligence
        watchlist = ["PLTR (Palantir)", "SOFI (SoFi)", "HOOD (Robinhood)", "ARM (ARM Holdings)"]
        investor_moves = ["Buffett: Recently added to Chubb (CB)", "Dalio: Warning on debt cycles"]
        world_events = ["Fed minutes suggest rates staying higher for longer", "Tech earnings season begins"]

        if final_recommendations:
            report_path = self.report_gen.generate_daily_report(
                final_recommendations,
                portfolio_value=real_val,
                liquid_cash=current_portfolio.cash,
                risk_reserve=risk_floor,
                strat_name=strat.name if strat else "N/A",
                strat_description=strat.description if strat else "N/A",
                gain_loss_abs=gain_loss_abs,
                gain_loss_pct=gain_loss_pct,
                watchlist=watchlist,
                investor_moves=investor_moves,
                world_events=world_events,
            )
            print(f"Report generated: {report_path}")
            print(f"Current Total Value: ${real_val:.2f}")
            print(f"Current Liquid Cash: ${current_portfolio.cash:.2f}")
            webbrowser.open(f"file://{os.path.abspath(report_path)}")
            self.exercise_recommendations(final_recommendations, current_portfolio, optimal_reserve)
            self.discovery.run_wiki_health_check()


if __name__ == "__main__":
    advisor = RealTimeAdvisor()
    advisor.run_morning_review()
