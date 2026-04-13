import structlog

from src.application.coordinator import StrategyOrchestrator
from src.domain.portfolio import Portfolio
from src.domain.strategy import TradingRule
from src.infrastructure.fs import FileSystemWikiAdapter
from src.infrastructure.llm import OllamaLLMAdapter
from src.simulator.engine import HistoricalSimulator

logger = structlog.get_logger()


def run_persona_competition():
    llm = OllamaLLMAdapter()
    fs = FileSystemWikiAdapter()
    orch = StrategyOrchestrator(llm, fs)

    # 1. Define the Universe for both
    # Buffett: Value/Moat | Day Trader: Momentum/Volatility
    universe = ["BRK-B", "AAPL", "KO", "GME", "AMC", "TSLA"]
    start_date = "2020-01-01"
    end_date = "2021-12-31"

    print("\n--- PERSONA COMPETITION: BUFFETT VS. DAY TRADER ($100 START) ---")
    print(f"Period: {start_date} to {end_date}\n")

    # 2. Formulate Strategies via Agents
    print("Formulating Buffett Strategy...")
    buffett_strat = orch.formulate_strategy(
        persona_path=".github/agents/strategy-agent.agent.md",
        context_topic="2020 Pandemic Value and Quality Moats",
        active_universe=["BRK-B", "AAPL", "KO"],
    )

    print("Formulating Day Trader Strategy...")
    day_trader_strat = orch.formulate_strategy(
        persona_path=".github/agents/day-trader.agent.md",
        context_topic="2021 Momentum and Meme Stock Volatility",
        active_universe=["GME", "AMC", "TSLA"],
    )

    # 3. Setup Simulator
    sim = HistoricalSimulator(tickers=universe, start_date=start_date, end_date=end_date)
    if not sim.load_data():
        return

    # 4. Initialize Portfolios
    p_buffett = Portfolio(name="Buffett-Portfolio", cash=100.0)
    p_day_trader = Portfolio(name="Day-Trader-Portfolio", cash=100.0)

    # 5. Run Simulations
    if buffett_strat:
        # Ensure it has a 'first_day' buy if LLM is too vague
        if not buffett_strat.rules:
            buffett_strat.rules.append(
                TradingRule(condition="first_day", action="Long-term Buy", params={"symbol": "BRK-B"})
            )
        sim.run_strategy(p_buffett, buffett_strat)

    if day_trader_strat:
        # Day Trader needs more action. If rules empty, give it a momentum-style start
        if not day_trader_strat.rules:
            day_trader_strat.rules.append(
                TradingRule(condition="first_day", action="Aggressive Entry", params={"symbol": "TSLA"})
            )
        sim.run_strategy(p_day_trader, day_trader_strat)

    # 6. Final Evaluation
    final_prices = sim.data.iloc[-1].to_dict()
    val_b = p_buffett.get_value(final_prices)
    val_dt = p_day_trader.get_value(final_prices)

    print("\n--- FINAL RESULTS ---")
    print(f"Buffett Value:    ${val_b:>8.2f} | Growth: {((val_b-100)/100)*100:>6.1f}%")
    print(f"Day Trader Value: ${val_dt:>8.2f} | Growth: {((val_dt-100)/100)*100:>6.1f}%")

    winner = "Buffett" if val_b > val_dt else "Day Trader"
    print(f"\nWINNER: {winner} 🏆")
    print(f"Buffett Trades: {len(p_buffett.history)}")
    print(f"Day Trader Trades: {len(p_day_trader.history)}")
    print("----------------------\n")


if __name__ == "__main__":
    run_persona_competition()
