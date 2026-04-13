import requests
from bs4 import BeautifulSoup
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.ports import ScraperPort
from src.domain.research import ResearchDocument


class PoliteWebScraperAdapter(ScraperPort):
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
            # In a full implementation, we'd use structlog here
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_headlines(self, source_url: str = "https://www.cnbc.com/world-markets/") -> str | None:
        """
        Fetches current market headlines to provide 'Today' context.
        """
        try:
            response = requests.get(source_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Simple extraction of headlines
            headlines = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])[:20]]
            return "\n".join(headlines)
        except Exception as e:
            print(f"Error fetching headlines: {e}")
            return None
