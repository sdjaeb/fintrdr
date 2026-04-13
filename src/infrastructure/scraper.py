import requests
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.research import ResearchDocument


class PoliteWebScraperAdapter:
    """
    Ingests web content politely with retries and exponential backoff.
    """

    def __init__(self, user_agent: str = "fintrdr-research-bot/1.0"):
        self.headers = {"User-Agent": user_agent}

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(requests.exceptions.RequestException),
    )
    def fetch_url(self, url: str) -> ResearchDocument | None:
        """
        Fetches and extracts text from a URL.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            raw_title = soup.title.string if soup.title else url
            title = str(raw_title) if raw_title else url

            return ResearchDocument(source_url=url, title=title, raw_content=text)
        except requests.exceptions.RequestException as e:
            # Structlog will be better here, but print for now
            print(f"Error fetching {url}: {e}")
            raise
