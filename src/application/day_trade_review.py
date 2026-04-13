import structlog

from src.application.coordinator import StrategyOrchestrator
from src.application.services import TickerDiscoveryService
from src.infrastructure.fs import FileSystemWikiAdapter
from src.infrastructure.llm import OllamaLLMAdapter

logger = structlog.get_logger()


def run_day_trader_review():
    llm = OllamaLLMAdapter()
    fs = FileSystemWikiAdapter()
    discovery = TickerDiscoveryService(fs, llm)
    orch = StrategyOrchestrator(llm, fs)

    print("\n--- DAY TRADER AGGRESSIVE SCAN ---")

    # 1. Discover Penny/Volatile Stocks
    volatile_universe = discovery.discover_volatile_tickers()
    if not volatile_universe:
        volatile_universe = ["MULN", "GME", "AMC", "ZOM"]  # Manual fallback for testing

    print(f"Scanning Volatile Universe: {volatile_universe}")

    # 2. Formulate Aggressive Strategy
    strat = orch.formulate_strategy(
        persona_path=".github/agents/day-trader.agent.md",
        context_topic="High Momentum and Shorting Opportunities",
        active_universe=volatile_universe,
    )

    if strat:
        print(f"\n--- Strategy: {strat.name} ---")
        print(f"Logic: {strat.description}")
        print("\nRECOMMENDED MOVES (ROBINHOOD-STYLE FRACTIONAL):")
        for rule in strat.rules:
            symbol = rule.params.get("symbol", "N/A")
            print(f"- {rule.action} {symbol} | Condition: {rule.condition}")


if __name__ == "__main__":
    run_day_trader_review()
