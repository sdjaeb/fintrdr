import json
import os
from datetime import datetime
from urllib.parse import urlparse

from src.domain.ports import WikiStoragePort
from src.domain.research import ResearchDocument, WikiArticle
from src.domain.strategy import InvestmentStrategy


class FileSystemWikiAdapter(WikiStoragePort):
    """
    Handles reading and writing to the local file system (Karpathy style wiki).
    """

    def __init__(self, base_dir: str = "."):
        self.research_dir = os.path.join(base_dir, "research")
        self.kb_dir = os.path.join(base_dir, "knowledge-base")
        self.strategy_dir = os.path.join(base_dir, "src/infrastructure/data/strategies")
        self.index_path = os.path.join(self.kb_dir, "Wiki Index.md")
        self.manifest_path = os.path.join(self.research_dir, ".processed_manifest.json")

        os.makedirs(self.research_dir, exist_ok=True)
        os.makedirs(self.kb_dir, exist_ok=True)
        os.makedirs(self.strategy_dir, exist_ok=True)

    def _load_manifest(self) -> dict[str, str]:
        if not os.path.exists(self.manifest_path):
            return {}
        with open(self.manifest_path, encoding="utf-8") as f:
            data = json.load(f)
            return dict(data) if isinstance(data, dict) else {}

    def _save_manifest(self, manifest: dict[str, str]) -> None:
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=4)

    def mark_as_processed(self, filepath: str) -> None:
        manifest = self._load_manifest()
        # Use filename as key, store timestamp
        manifest[os.path.basename(filepath)] = datetime.now().isoformat()
        self._save_manifest(manifest)

    def list_unprocessed_research(self, processed_urls: list[str]) -> list[str]:
        """
        Returns a list of raw research files that haven't been summarized into the wiki yet.
        """
        manifest = self._load_manifest()
        all_files = [f for f in os.listdir(self.research_dir) if f.endswith(".txt")]
        unprocessed = [os.path.join(self.research_dir, f) for f in all_files if f not in manifest]
        return unprocessed

    def save_raw_research(self, doc: ResearchDocument) -> str:
        """
        Saves a raw ingested document to the research folder.
        """
        parsed_url = urlparse(doc.source_url)
        safe_name = parsed_url.netloc + parsed_url.path.replace("/", "_")
        if not safe_name.endswith(".txt"):
            safe_name += ".txt"

        filepath = os.path.join(self.research_dir, safe_name)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Source: {doc.source_url}\n")
            f.write(f"Title: {doc.title}\n")
            f.write(f"Ingested: {doc.ingested_at.isoformat()}\n\n")
            f.write(doc.raw_content)

        return filepath

    def read_file(self, filepath: str) -> str:
        """
        Read content of a file.
        """
        with open(filepath, encoding="utf-8") as f:
            return f.read()

    def read_index(self) -> str:
        """
        Reads the central Wiki Index file for the LLM to use as context.
        """
        if not os.path.exists(self.index_path):
            return "# Wiki Index\n\nEmpty."

        with open(self.index_path, encoding="utf-8") as f:
            return f.read()

    def write_wiki_article(self, article: WikiArticle, filename: str) -> str:
        """
        Writes a structured WikiArticle to the knowledge base.
        """
        if not filename.endswith(".md"):
            filename += ".md"

        filepath = os.path.join(self.kb_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {article.title}\n\n")

            f.write("## Sources\n")
            for source in article.sources:
                f.write(f"- [[{source}]]\n")
            f.write("\n")

            f.write("## Summary\n")
            f.write(f"{article.summary}\n\n")

            f.write("## Concepts\n")
            f.write(f"{article.content}\n\n")

            f.write("## Backlinks\n")
            for link in article.backlinks:
                f.write(f"- [[{link}]]\n")

        return filepath

    def write_index(self, content: str) -> None:
        """
        Overwrites the Wiki Index with the LLM's new version.
        """
        with open(self.index_path, "w", encoding="utf-8") as f:
            f.write(content)

    def save_strategy(self, strategy: InvestmentStrategy) -> str:
        """
        Saves a formulated strategy to the strategies folder.
        """
        filename = f"{strategy.name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.strategy_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(strategy.model_dump_json(indent=4))
        return filepath

    def load_strategy(self, name: str) -> InvestmentStrategy | None:
        """
        Loads a strategy by name.
        """
        filename = f"{name.lower().replace(' ', '_')}.json"
        filepath = os.path.join(self.strategy_dir, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath, encoding="utf-8") as f:
            return InvestmentStrategy.model_validate_json(f.read())
