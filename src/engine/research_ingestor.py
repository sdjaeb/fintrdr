import os
from datetime import datetime
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class ResearchIngestor:
    """
    Ingests raw research from URLs, GitHub repos, and documents.
    """

    def __init__(self, research_dir: str = "research"):
        self.research_dir = research_dir
        os.makedirs(self.research_dir, exist_ok=True)

    def fetch_url(self, url: str) -> str | None:
        """
        Fetches content from a URL and saves it to a local markdown file.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            # Basic text extraction - to be improved with specialized parsers
            text = soup.get_text(separator="\n")

            parsed_url = urlparse(url)
            filename = parsed_url.netloc + parsed_url.path.replace("/", "_") + ".txt"
            filepath = os.path.join(self.research_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Source: {url}\n\n")
                f.write(text)

            print(f"Ingested: {url} -> {filepath}")
            return filepath
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def fetch_headlines(self, source_url: str = "https://www.cnbc.com/world-markets/") -> str | None:
        """
        Fetches current market headlines to provide 'Today' context.
        Implements a 4-hour 'cooldown' to prevent pollution from rapid successive runs.
        """
        filename = f"today_headlines_{datetime.now().strftime('%Y%m%d')}.txt"
        filepath = os.path.join(self.research_dir, filename)

        # Check if we already have a recent fetch
        if os.path.exists(filepath):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            age = datetime.now() - file_mod_time
            if age.total_seconds() < 14400:  # 4 hours
                print(f"Using cached headlines (Age: {age.total_seconds()/60:.1f} mins)")
                return filepath

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(source_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Simple extraction of headlines
            headlines = [h.get_text(strip=True) for h in soup.find_all(["h2", "h3"])[:20]]
            content = "\n".join(headlines)

            filename = f"today_headlines_{datetime.now().strftime('%Y%m%d')}.txt"
            filepath = os.path.join(self.research_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Source: {source_url}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n\n")
                f.write("CURRENT HEADLINES:\n")
                f.write(content)

            print(f"Ingested Today's Headlines: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error fetching headlines: {e}")
            return None


if __name__ == "__main__":
    ingestor = ResearchIngestor()
    # Test with some initial research
    ingestor.fetch_url("https://en.wikipedia.org/wiki/Warren_Buffett")
    ingestor.fetch_url("https://en.wikipedia.org/wiki/Ray_Dalio")
