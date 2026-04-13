import json
import os
import time
import uuid
from datetime import datetime

import structlog

from src.domain.ports import LLMPort, ScraperPort, WikiStoragePort
from src.domain.research import WikiArticle
from src.domain.telemetry import WikiLoopTelemetry

logger = structlog.get_logger()


class ResearchIngestionService:
    def __init__(self, scraper: ScraperPort, storage: WikiStoragePort):
        self.scraper = scraper
        self.storage = storage

    def ingest_urls(self, urls: list[str]) -> None:
        """
        Ingests URLs and saves them as raw research documents.
        """
        for url in urls:
            try:
                doc = self.scraper.fetch_url(url)
                if doc:
                    path = self.storage.save_raw_research(doc)
                    logger.info("Ingested URL", url=url, path=path)
            except Exception as e:
                logger.error("Failed to ingest URL", url=url, error=str(e))


class TickerDiscoveryService:
    """
    Scans the Knowledge Base to discover and validate new tickers.
    Manages both 'Active' and 'Watchlist' tiers.
    """

    def __init__(self, storage: WikiStoragePort, llm: LLMPort):
        self.storage = storage
        self.llm = llm
        # Paths are managed by the storage port, but service knows the concept
        self.universe_path = "src/infrastructure/data/universe/ticker_universe.json"
        self.watchlist_path = "src/infrastructure/data/universe/ticker_watchlist.json"

    def discover_tickers_from_wiki(self) -> list[str]:
        """
        Reads all Wiki articles in the knowledge base to extract and validate ticker symbols.
        """
        logger.info("Discovering tickers from all Wiki articles")
        # This is a bit of a leak, ideally storage port handles listing
        kb_dir = "knowledge-base"
        try:
            kb_files = [f for f in os.listdir(kb_dir) if f.endswith(".md") and f != "Wiki Index.md"]

            all_content = ""
            for f in kb_files:
                all_content += self.storage.read_file(os.path.join(kb_dir, f)) + "\n\n"

            if not all_content:
                logger.info("No wiki content found to analyze.")
                return []
        except Exception as e:
            logger.error("Failed to read wiki content", error=str(e))
            return []

        prompt = (
            f"You are a sophisticated financial analyst. Read the following Knowledge Base content:\n{all_content[:6000]}\n\n"
            "Your goal is to build a high-conviction ticker universe across STOCKS and CRYPTO. "
            "1. Identify any specific stock ticker symbols mentioned (e.g., TSLA, AAPL).\n"
            "2. Identify any crypto-assets or coins mentioned (e.g., Bitcoin -> BTC-USD, Ethereum -> ETH-USD).\n"
            "3. For any companies or coins mentioned without tickers, look up or provide their common ticker symbol.\n"
            "4. For the investors mentioned, include their primary fund or vehicle tickers (e.g., Berkshire -> BRK-B, ARK -> ARKK, Magellan -> FMAGX).\n\n"
            "Return ONLY a JSON list of strings containing the ticker symbols."
        )

        try:
            response = self.llm.generate(prompt, system_prompt="You return only a JSON list of strings.")
            cleaned = response.strip()
            if "```" in cleaned:
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[-1].split("```")[0]
                else:
                    cleaned = cleaned.split("```")[-1].split("```")[0]

            start_idx = cleaned.find("[")
            end_idx = cleaned.rfind("]")
            if start_idx != -1 and end_idx != -1:
                cleaned = cleaned[start_idx : end_idx + 1]

            discovered = json.loads(cleaned)
            if not isinstance(discovered, list):
                return []

            valid_tickers = [t.upper() for t in discovered if isinstance(t, str)]
            self.update_universe(valid_tickers)
            return valid_tickers

        except Exception as e:
            logger.error("Ticker discovery failed", error=str(e))
            return []

    def discover_volatile_tickers(self) -> list[str]:
        """
        Specifically looks for low-priced, high-momentum tickers in the Wiki and news.
        """
        try:
            all_content = ""
            kb_dir = "knowledge-base"
            kb_files = [f for f in os.listdir(kb_dir) if f.endswith(".md")]
            for f in kb_files:
                all_content += self.storage.read_file(os.path.join(kb_dir, f)) + "\n"
        except Exception as e:
            logger.error("Failed to read wiki for volatile discovery", error=str(e))
            return []

        prompt = (
            f"You are a Day Trader scanning for opportunities. Read this content:\n{all_content[:4000]}\n\n"
            "Identify any mentioned penny stocks (price < $5), micro-cap companies, or highly volatile tickers. "
            "Return ONLY a JSON list of strings."
        )
        try:
            response = self.llm.generate(prompt, system_prompt="You return ONLY a JSON list.")
            cleaned = response.strip()
            if "```" in cleaned:
                cleaned = cleaned.split("```")[-1].split("```")[0].strip()
            return json.loads(cleaned)
        except Exception:
            return []

    def manage_universe(self, trajectories: dict[str, str]) -> dict[str, list[str]]:
        """
        Reviews Active vs. Watchlist and recommends promotions/demotions.
        """
        logger.info("Managing Ticker Universe and Watchlist Tiering")

        try:
            current_active = []
            if os.path.exists(self.universe_path):
                with open(self.universe_path) as f:
                    current_active = json.load(f)

            current_watch = []
            if os.path.exists(self.watchlist_path):
                with open(self.watchlist_path) as f:
                    current_watch = json.load(f)
            else:
                current_watch = ["PLTR", "SOFI", "HOOD", "ARM"]

            to_promote = [t for t in current_watch if trajectories.get(t, "").startswith("UPWARD")]
            to_demote = [t for t in current_active if trajectories.get(t, "").startswith("DOWNWARD")]

            new_active = list(set([t for t in current_active if t not in to_demote] + to_promote))
            new_watch = list(set([t for t in current_watch if t not in to_promote] + to_demote))

            with open(self.universe_path, "w") as f:
                json.dump(new_active, f, indent=4)
            with open(self.watchlist_path, "w") as f:
                json.dump(new_watch, f, indent=4)

            if to_promote:
                logger.info("Tickers PROMOTED to Active Universe", tickers=to_promote)
            if to_demote:
                logger.info("Tickers DEMOTED to Watchlist", tickers=to_demote)

            return {"promoted": to_promote, "demoted": to_demote}
        except Exception as e:
            logger.error("Universe management failed", error=str(e))
            return {"promoted": [], "demoted": []}

    def update_universe(self, new_tickers: list[str]) -> None:
        """
        Saves discovered tickers to universe. Moves low-confidence to watchlist.
        """
        try:
            current_universe = []
            if os.path.exists(self.universe_path):
                with open(self.universe_path) as f:
                    current_universe = json.load(f)

            updated = list(set(current_universe + new_tickers))
            with open(self.universe_path, "w") as f:
                json.dump(updated, f, indent=4)
            logger.info("Ticker Universe updated", total_count=len(updated))
        except Exception as e:
            logger.error("Universe update failed", error=str(e))

    def run_wiki_health_check(self) -> dict | None:
        """
        Karpathy Point #7 & #9: Self-improving loop and health checks.
        Scans the wiki to find inconsistencies and missing connections.
        """
        logger.info("Starting Wiki Health Check (Linter)")
        index_content = self.storage.read_index()

        prompt = (
            f"You are a Knowledge Base Auditor. Review this Wiki Index and structure:\n{index_content}\n\n"
            "Identify:\n"
            "1. GAPS: What financial concepts or investors are mentioned but don't have articles?\n"
            "2. LINKS: Which articles should be linked but aren't? (e.g. 'Ray Dalio' should link to '2008 Crisis')\n"
            "3. DISCOVERY: Suggest 3 new URLs or topics to research to strengthen the engine.\n\n"
            "Return a JSON object with keys: 'gaps', 'missing_links', 'suggestions'."
        )

        try:
            response = self.llm.generate(prompt, system_prompt="You return ONLY valid JSON.")

            # Robust extraction logic
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

            def to_str(val):
                if isinstance(val, dict | list):
                    return json.dumps(val, indent=2)
                return str(val)

            # Save findings as a new Wiki Article for the human/agents to see
            health_article = WikiArticle(
                title=to_str(data.get("title", f"Wiki Health Audit {datetime.now().strftime('%Y-%m-%d')}")),
                summary="Automated linter pass to identify knowledge gaps and link opportunities.",
                content=f"## Identified Gaps\n{to_str(data.get('gaps', []))}\n\n"
                f"## Link Recommendations\n{to_str(data.get('missing_links', []))}\n\n"
                f"## Future Research\n{to_str(data.get('suggestions', []))}",
                sources=["Wiki Internal Linter"],
                backlinks=["Wiki Index"],
            )
            self.storage.write_wiki_article(health_article, f"wiki_health_audit_{datetime.now().strftime('%Y%m%d')}.md")
            logger.info("Wiki Health Audit complete.")
            return data
        except Exception as e:
            logger.error("Wiki Health Check failed", error=str(e))
            return None


class WikiMaintenanceService:
    def __init__(self, storage: WikiStoragePort, llm: LLMPort):
        self.storage = storage
        self.llm = llm

    def run_karpathy_loop(self) -> WikiLoopTelemetry:
        """
        The core of the system:
        1. Reads index to find what's missing or what's new.
        2. Summarizes new raw data into Wiki Articles.
        3. Updates the index.
        """
        iteration_id = str(uuid.uuid4())
        telemetry = WikiLoopTelemetry(iteration_id=iteration_id)
        logger.info("Starting Karpathy Wiki Loop", iteration_id=iteration_id)

        try:
            index_content = self.storage.read_index()
            unprocessed_files = self.storage.list_unprocessed_research(processed_urls=[])

            if not unprocessed_files:
                logger.info("No new research to process.")
                telemetry.status = "no_files"
                telemetry.end_time = datetime.now()
                return telemetry

            for file_to_process in unprocessed_files:
                # Double-check manifest inside the loop to handle rapid state changes
                # Note: storage port should ideally handle this check
                raw_content = self.storage.read_file(file_to_process)
                logger.info("Processing raw research", file=file_to_process)

                prompt = (
                    "You are a knowledge base maintainer. Read the following raw research "
                    "and extract the main concepts. Format your response strictly as a JSON object "
                    "with keys: 'title', 'summary', 'content', 'sources' (list of strings), "
                    "and 'backlinks' (list of strings).\n\n"
                    f"Raw Content:\n{raw_content[:2000]}..."
                )

                start_llm = time.perf_counter()
                response = self.llm.generate(prompt, system_prompt="You return only valid JSON.")
                telemetry.ollama_response_time_ms += (time.perf_counter() - start_llm) * 1000

                try:
                    cleaned_response = response.strip()
                    if "```" in cleaned_response:
                        if "```json" in cleaned_response:
                            cleaned_response = cleaned_response.split("```json")[-1].split("```")[0]
                        else:
                            cleaned_response = cleaned_response.split("```")[-1].split("```")[0]

                    start_idx = cleaned_response.find("{")
                    end_idx = cleaned_response.rfind("}")
                    if start_idx != -1 and end_idx != -1:
                        cleaned_response = cleaned_response[start_idx : end_idx + 1]

                    data = json.loads(cleaned_response)

                    def to_str(val):
                        if isinstance(val, dict | list):
                            return json.dumps(val, indent=2)
                        return str(val)

                    article = WikiArticle(
                        title=to_str(data.get("title", "Untitled Concept")),
                        summary=to_str(data.get("summary", "No summary provided.")),
                        content=to_str(data.get("content", "No content provided.")),
                        sources=data.get("sources", [file_to_process]),
                        backlinks=data.get("backlinks", ["Wiki Index"]),
                    )

                    filename = f"{article.title.lower().replace(' ', '_')}.md"
                    self.storage.write_wiki_article(article, filename)
                    logger.info("Wrote Wiki Article", title=article.title, filename=filename)
                    self.storage.mark_as_processed(file_to_process)
                    telemetry.files_processed += 1

                    update_prompt = (
                        f"You are maintaining a Wiki Index. Here is the current index:\n{index_content}\n\n"
                        f"Please update it to include a link to the new article: [[{article.title}]]. "
                        "Return the entire updated Markdown index."
                    )
                    index_content = self.llm.generate(update_prompt)
                    self.storage.write_index(index_content)
                    logger.info("Updated Wiki Index with", title=article.title)

                except json.JSONDecodeError as jde:
                    logger.error("Failed to decode JSON from Ollama", raw_response=response, error=str(jde))
                    continue

            telemetry.status = "completed"

        except Exception as e:
            logger.error("Error in Karpathy Loop", error=str(e))
            telemetry.status = "failed"
            telemetry.error_message = str(e)

        telemetry.end_time = datetime.now()
        logger.info("Finished Karpathy Wiki Loop", status=telemetry.status, duration=telemetry.duration_seconds)
        return telemetry
