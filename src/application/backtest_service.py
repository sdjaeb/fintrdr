from datetime import datetime, timedelta

import structlog

from src.domain.portfolio import Portfolio
from src.domain.strategy import InvestmentStrategy, TradingRule
from src.simulator.engine import HistoricalSimulator

logger = structlog.get_logger()


class ShadowBacktestService:
    """
    Runs short-term (6-month) simulations on candidates to 'test' them
    before promotion to the active universe.
    """

    def __init__(self):
        pass

    def run_shadow_test(self, ticker: str):
        """
        Replays the last 180 days for a specific ticker.
        """
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")

        logger.info("Running Shadow Backtest", ticker=ticker, period="6 Months")

        sim = HistoricalSimulator(tickers=[ticker], start_date=start_date, end_date=end_date)
        if not sim.load_data():
            return None

        p = Portfolio(name=f"Shadow-Test-{ticker}", cash=100.0)

        # Simple 'Baseline Buy' Strategy for testing
        strat = InvestmentStrategy(
            name=f"Shadow Test: {ticker}",
            description="Automatic buy-on-first-day shadow test.",
            target_tickers=[ticker],
            rules=[TradingRule(condition="first_day", action="BUY", params={"symbol": ticker})],
            agent_source="ShadowBacktester",
        )

        sim.run_strategy(p, strat)

        final_prices = sim.data.iloc[-1].to_dict()
        final_val = p.get_value(final_prices)

        result = {
            "ticker": ticker,
            "final_value": round(final_val, 2),
            "growth_pct": round(((final_val - 100) / 100) * 100, 2),
            "trades": len(p.history),
        }
        logger.info("Shadow Test Complete", result=result)
        return result


if __name__ == "__main__":
    tester = ShadowBacktestService()
    # Test on a watchlist candidate
    tester.run_shadow_test("PLTR")
