from abc import ABC, abstractmethod
from typing import Any

from src.domain.research import ResearchDocument, WikiArticle
from src.domain.strategy import InvestmentStrategy


class LLMPort(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Generates text using an LLM."""
        pass


class WikiStoragePort(ABC):
    @abstractmethod
    def save_raw_research(self, doc: ResearchDocument) -> str:
        """Saves raw research to storage."""
        pass

    @abstractmethod
    def list_unprocessed_research(self, processed_urls: list[str]) -> list[str]:
        """Lists research files not yet in the wiki."""
        pass

    @abstractmethod
    def read_file(self, filepath: str) -> str:
        """Reads a file from storage."""
        pass

    @abstractmethod
    def read_index(self) -> str:
        """Reads the central wiki index."""
        pass

    @abstractmethod
    def write_wiki_article(self, article: WikiArticle, filename: str) -> str:
        """Writes a synthesized article to the wiki."""
        pass

    @abstractmethod
    def write_index(self, content: str) -> None:
        """Overwrites the wiki index."""
        pass

    @abstractmethod
    def save_strategy(self, strategy: InvestmentStrategy) -> str:
        """Saves an investment strategy."""
        pass

    @abstractmethod
    def load_strategy(self, name: str) -> InvestmentStrategy | None:
        """Loads an investment strategy."""
        pass

    @abstractmethod
    def mark_as_processed(self, filepath: str) -> None:
        """Marks a research file as processed."""
        pass


class ScraperPort(ABC):
    @abstractmethod
    def fetch_url(self, url: str) -> ResearchDocument | None:
        """Fetches and parses a URL into a ResearchDocument."""
        pass

    @abstractmethod
    def fetch_headlines(self, source_url: str = "https://www.cnbc.com/world-markets/") -> str | None:
        """Fetches current market headlines."""
        pass


class ReportingPort(ABC):
    @abstractmethod
    def generate_daily_report(
        self,
        recommendations: list[dict[str, Any]],
        portfolio_value: float = 100.0,
        liquid_cash: float = 0.0,
        risk_reserve: float = 0.0,
        strat_name: str = "N/A",
        strat_description: str = "N/A",
        gain_loss_pct: float = 0.0,
        gain_loss_abs: float = 0.0,
        watchlist: list[str] | None = None,
        investor_moves: list[str] | None = None,
        world_events: list[str] | None = None,
    ) -> str:
        """Generates MD and HTML reports."""
        pass
