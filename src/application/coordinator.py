import json

import structlog

from src.domain.strategy import InvestmentStrategy, TradingRule
from src.infrastructure.fs import FileSystemWikiAdapter
from src.infrastructure.llm import OllamaLLMAdapter

logger = structlog.get_logger()


class StrategyOrchestrator:
    """
    Coordinator that reads the Knowledge Base and formulates strategies.
    """

    def __init__(self, llm: OllamaLLMAdapter, fs: FileSystemWikiAdapter):
        self.llm = llm
        self.fs = fs

    def formulate_strategy(
        self, persona_path: str, context_topic: str, active_universe: list[str]
    ) -> InvestmentStrategy | None:
        """
        Loads a persona and the relevant Wiki context to generate a strategy.
        Strictly limits the agent to the 'active_universe' of tickers.
        """
        logger.info("Formulating new strategy", topic=context_topic, universe_size=len(active_universe))

        # 1. Load Persona
        with open(persona_path, encoding="utf-8") as f:
            persona = f.read()

        # 2. Load Wiki Index
        wiki_index = self.fs.read_index()

        # 3. Prompt the LLM
        prompt = (
            f"Persona Instructions:\n{persona}\n\n"
            f"Knowledge Base Index:\n{wiki_index}\n\n"
            f"ACTIVE TICKER UNIVERSE: {active_universe}\n\n"
            f"Goal: Formulate a DIVERSIFIED investment strategy for '{context_topic}'.\n"
            f"CRITICAL REQUIREMENTS:\n"
            f"1. DIVERSIFICATION: You MUST select 3-5 UNIQUE and DIFFERENT tickers from the universe. Do not put all rules on one symbol.\n"
            f"2. ACTION CATEGORIES: Every rule must have a 'timing' field. \n"
            f"   - 'IMMEDIATE': For a buy/sell action to take RIGHT NOW (Condition should be 'first_day').\n"
            f"   - 'CONTINGENT': For a future trigger (e.g., 'price < X' or 'price breaks resistance').\n"
            f"3. JSON SCHEMA: Return a JSON object with: 'name', 'description', 'target_tickers', "
            f"'rules' (list of {{'condition', 'action', 'params', 'timing'}}), and 'agent_source'.\n"
            f"In 'params', always include {{'symbol': 'TICKER'}}."
        )

        try:
            response = self.llm.generate(prompt, system_prompt="You return only valid JSON.")

            # Use same cleaning logic as Karpathy Loop
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                cleaned_response = cleaned_response.split("\n", 1)[-1]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response.rsplit("```", 1)[0]
            cleaned_response = cleaned_response.strip()

            data = json.loads(cleaned_response)

            def to_str(val):
                if isinstance(val, dict | list):
                    return json.dumps(val, indent=2)
                return str(val)

            rules = [TradingRule(**r) for r in data.get("rules", [])]
            strategy = InvestmentStrategy(
                name=to_str(data.get("name", "Unnamed Strategy")),
                description=to_str(data.get("description", "No description.")),
                target_tickers=data.get("target_tickers", []),
                rules=rules,
                agent_source=data.get("agent_source", "Unknown Agent"),
            )

            logger.info("Strategy Formulated", name=strategy.name, tickers=strategy.target_tickers)
            return strategy

        except Exception as e:
            logger.error("Failed to formulate strategy", error=str(e))
            return None


if __name__ == "__main__":
    from src.domain.portfolio import Portfolio
    from src.simulator.engine import HistoricalSimulator

    # Initialize Adapters
    llm = OllamaLLMAdapter()
    fs = FileSystemWikiAdapter()
    orch = StrategyOrchestrator(llm, fs)

    # 1. Define Ticker Universe (SPY = S&P 500, QQQ = Nasdaq, BRK-B = Buffett)
    universe = ["SPY", "QQQ", "BRK-B", "AAPL", "MSFT"]

    # 2. Formulate Strategy
    strat = orch.formulate_strategy(
        persona_path=".github/agents/strategy-agent.agent.md",
        context_topic="Post-Bubble Recovery (Early 2000s)",
        active_universe=universe,
    )

    if strat:
        # 3. Save Strategy
        fs.save_strategy(strat)

        # 4. Execute Strategy in Simulator
        sim = HistoricalSimulator(tickers=universe, start_date="2002-01-01", end_date="2004-12-31")
        if sim.load_data():
            p = Portfolio(name="Autonomous-Universe-Portfolio", cash=10000.0)

            sim.run_strategy(p, strat)

            print(f"\n--- Results for {strat.name} ---")
            print(f"Final Portfolio Value: ${p.get_value(sim.data.iloc[-1].to_dict()):.2f}")
            print(f"Trade History: {len(p.history)} trades executed.")
