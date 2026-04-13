import json

import structlog

from src.infrastructure.llm import OllamaLLMAdapter

logger = structlog.get_logger()


def discover_new_universe():
    llm = OllamaLLMAdapter()

    current_universe = ["NVDA", "GOOGL", "AMZN", "TSLA", "AAPL"]
    prompt = (
        "You are a Senior Market Researcher. The user wants to expand the ticker universe for a new $100 -> $1B portfolio journey.\n\n"
        "Please identify the following tickers:\n"
        "1. 10 STABLE/BLUE-CHIP SYMBOLS (e.g., MSFT, JNJ, V).\n"
        "2. 20 PENNY STOCKS (Price < $5, high potential volatility/momentum).\n"
        "3. 10 PROMISING NEW IPOs (Companies that went public in the last 12-24 months).\n\n"
        "Return the result STRICTLY as a JSON object with keys: 'stable', 'penny', 'ipo'. "
        "Each value should be a list of ticker symbols."
    )

    try:
        response = llm.generate(prompt, system_prompt="You return ONLY JSON.")

        # Clean response
        cleaned = response.strip()
        if "```" in cleaned:
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[-1].split("```")[0]
            else:
                cleaned = cleaned.split("```")[-1].split("```")[0]

        start_idx = cleaned.find("{")
        end_idx = cleaned.rfind("}")
        if start_idx != -1 and end_idx != -1:
            cleaned = cleaned[start_idx : end_idx + 1]

        data = json.loads(cleaned)

        all_new = data.get("stable", []) + data.get("penny", []) + data.get("ipo", [])
        final_universe = list(set(current_universe + all_new))

        # Filter for basic ticker validity (1-5 chars)
        final_universe = [t.upper().strip() for t in final_universe if isinstance(t, str) and 1 <= len(t) <= 5]

        universe_path = "src/simulator/data/ticker_universe.json"
        with open(universe_path, "w") as f:
            json.dump(final_universe, f, indent=4)

        print(f"Universe expanded to {len(final_universe)} tickers.")
        print(
            f"Categories discovered: Stable: {len(data.get('stable', []))}, Penny: {len(data.get('penny', []))}, IPO: {len(data.get('ipo', []))}"
        )
        return final_universe

    except Exception as e:
        logger.error("Discovery failed", error=str(e))
        return current_universe


if __name__ == "__main__":
    discover_new_universe()
