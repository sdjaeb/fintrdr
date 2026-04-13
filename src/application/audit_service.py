import json

import structlog

from src.domain.research import WikiArticle
from src.infrastructure.fs import FileSystemWikiAdapter
from src.infrastructure.llm import OllamaLLMAdapter

logger = structlog.get_logger()


class DeepAuditService:
    """
    Correlates our current ticker universe with historical events found in the Wiki.
    """

    def __init__(self, fs: FileSystemWikiAdapter, llm: OllamaLLMAdapter):
        self.fs = fs
        self.llm = llm

    def run_correlation_audit(self, universe: list[str]):
        """
        Creates 'Correlation Map' articles in the Wiki.
        """
        logger.info("Starting Deep Audit: Correlation Mapping")

        wiki_index = self.fs.read_index()

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
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1:
                cleaned = cleaned[start_idx : end_idx + 1]

            data = json.loads(cleaned)
            article = WikiArticle(
                title=data.get("title", "Ticker-Event Correlation Map"),
                summary="Mapping current universe to historical wiki events.",
                content=data.get("content", "No content provided."),
                sources=["Wiki Index", "Investor Profiles"],
                backlinks=["Wiki Index", "2008 Financial Crisis"],
            )

            self.fs.write_wiki_article(article, "ticker_event_correlation_map.md")
            logger.info("Correlation Audit complete and saved to Wiki.")

        except Exception as e:
            logger.error("Deep Audit failed", error=str(e))


if __name__ == "__main__":
    llm = OllamaLLMAdapter()
    fs = FileSystemWikiAdapter()
    audit = DeepAuditService(fs, llm)
    with open("src/simulator/data/ticker_universe.json") as f:
        uni = json.load(f)
    audit.run_correlation_audit(uni)
