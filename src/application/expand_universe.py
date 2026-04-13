import json

import structlog

from src.infrastructure.llm import OllamaLLMAdapter

logger = structlog.get_logger()


def expand_simons_universe():
    llm = OllamaLLMAdapter()

    prompt = (
        "You are a Quant Researcher specializing in Jim Simons' techniques. "
        "Expand our ticker universe with 20 high-alpha targets:\n"
        "1. 5 Inverse/Leveraged ETFs (e.g., TQQQ, SQQQ, SOXL) for volatility harvesting.\n"
        "2. 5 Global Leaders (e.g., ASML, TSM, BABA) for geographic arbitrage.\n"
        "3. 5 Commodity Proxies (e.g., GLD, SLV, GDX) for macro correlation.\n"
        "4. 5 High-Volatility Mathematical Plays (Stocks with historically high beta/mean reversion).\n\n"
        "Return ONLY a JSON list of strings."
    )

    try:
        response = llm.generate(prompt, system_prompt="You return ONLY a JSON list of strings.")

        # Robust cleaning
        cleaned = response.strip()
        start_idx = cleaned.find("[")
        end_idx = cleaned.rfind("]")
        if start_idx != -1 and end_idx != -1:
            cleaned = cleaned[start_idx : end_idx + 1]

        new_tickers = json.loads(cleaned)

        universe_path = "src/simulator/data/ticker_universe.json"
        with open(universe_path) as f:
            current = json.load(f)

        updated = list(set(current + new_tickers))
        # Basic validation
        updated = [t.upper().strip() for t in updated if isinstance(t, str) and 1 <= len(t) <= 5]

        with open(universe_path, "w") as f:
            json.dump(updated, f, indent=4)

        print(f"✅ Universe expanded with Simons-style targets. Total Tickers: {len(updated)}")
        return updated

    except Exception as e:
        logger.error("Simons expansion failed", error=str(e))
        return []


if __name__ == "__main__":
    expand_simons_universe()
