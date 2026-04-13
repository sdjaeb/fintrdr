import structlog

from src.application.services import (
    ResearchIngestionService,
    TickerDiscoveryService,
    WikiMaintenanceService,
)
from src.infrastructure.fs import FileSystemWikiAdapter
from src.infrastructure.llm import OllamaLLMAdapter
from src.infrastructure.scraper import PoliteWebScraperAdapter

# Configure structured logging
structlog.configure()
logger = structlog.get_logger()


def main():
    # Initialize Adapters
    scraper = PoliteWebScraperAdapter()
    fs = FileSystemWikiAdapter()
    llm = OllamaLLMAdapter()  # Defaults to localhost:11434 and gemma4:e4b

    # Initialize Services
    ingestion_service = ResearchIngestionService(scraper, fs)
    maintenance_service = WikiMaintenanceService(fs, llm)
    discovery_service = TickerDiscoveryService(fs, llm)

    # 1. Ingest initial research if needed
    initial_urls = [
        "https://en.wikipedia.org/wiki/Warren_Buffett",
        "https://en.wikipedia.org/wiki/Ray_Dalio",
        "https://en.wikipedia.org/wiki/Jim_Simons_(mathematician)",
        "https://en.wikipedia.org/wiki/Cathie_Wood",
        "https://en.wikipedia.org/wiki/George_Soros",
        "https://en.wikipedia.org/wiki/Peter_Lynch",
    ]
    logger.info("Starting initial ingestion", urls=initial_urls)
    ingestion_service.ingest_urls(initial_urls)

    # 2. Run the Karpathy Wiki Loop (Synthesize Research)
    logger.info("Starting Karpathy Wiki Loop")
    maintenance_service.run_karpathy_loop()

    # 3. Discover Tickers from Knowledge Base
    logger.info("Starting Ticker Discovery")
    universe = discovery_service.discover_tickers_from_wiki()
    print(f"Discovered Ticker Universe: {universe}")

    # 4. (Optional) Run Strategy Orchestration based on new knowledge
    # ... strategy formulate ...


if __name__ == "__main__":
    main()
