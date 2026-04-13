import json

import structlog

from src.domain.ports import LLMPort, WikiStoragePort
from src.domain.research import WikiArticle

logger = structlog.get_logger()


class DeepAuditService:
    """
    Correlates our current ticker universe with historical events found in the Wiki.
    """

    def __init__(self, storage: WikiStoragePort, llm: LLMPort):
        self.storage = storage
        self.llm = llm

    def run_correlation_audit(self, universe: list[str]) -> None:
        """
        Creates 'Correlation Map' articles in the Wiki.
        """
        logger.info("Starting Deep Audit: Correlation Mapping")

        wiki_index = self.storage.read_index()

        prompt = (
            f"You are a Historical Financial Auditor. We are tracking these tickers: {universe}\n\n"
            f"Read our Knowledge Base Index:\n{wiki_index}\n\n"
            "Goal: Create a 'Ticker-Event Correlation Map'. "
            "For each ticker or its sector, identify a relevant historical event from the Wiki "
            "(e.g., '2008 Financial Crisis', '1997 Asian Crisis') and explain how that company/sector "
            "likely behaves during such an event.\n\n"
            "Format your response as a JSON WikiArticle with title 'Ticker-Event Correlation Map'."
        )

        try:
            response = self.llm.generate(prompt, system_prompt="You return only JSON.")
            # Robust extraction
            cleaned = response.strip()
            if cleaned.startswith("```"):
                if cleaned.startswith("```json"):
                    cleaned = cleaned.split("```json")[-1].split("```")[0]
                else:
                    cleaned = cleaned.split("```")[-1].split("```")[0]

            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1:
                cleaned = cleaned[start_idx : end_idx + 1]

            data = json.loads(cleaned)

            def to_str(val):
                if isinstance(val, dict | list):
                    return json.dumps(val, indent=2)
                return str(val)

            article = WikiArticle(
                title=to_str(data.get("title", "Ticker-Event Correlation Map")),
                summary="Mapping current universe to historical wiki events.",
                content=to_str(data.get("content", "No content provided.")),
                sources=["Wiki Index", "Investor Profiles"],
                backlinks=["Wiki Index", "2008 Financial Crisis"],
            )

            self.storage.write_wiki_article(article, "ticker_event_correlation_map.md")
            logger.info("Correlation Audit complete and saved to Wiki.")

        except Exception as e:
            logger.error("Deep Audit failed", error=str(e))
