from unittest.mock import MagicMock, patch

from src.application.services import ResearchIngestionService, TickerDiscoveryService, WikiMaintenanceService
from src.domain.research import ResearchDocument


def test_ingestion_service():
    scraper = MagicMock()
    storage = MagicMock()
    svc = ResearchIngestionService(scraper, storage)
    scraper.fetch_url.return_value = ResearchDocument(source_url="u", title="T", raw_content="C")
    svc.ingest_urls(["u"])
    assert storage.save_raw_research.called

    scraper.fetch_url.side_effect = Exception("Fail")
    svc.ingest_urls(["u2"])  # Cover exception


def test_discovery_wiki_content():
    storage = MagicMock()
    llm = MagicMock()
    svc = TickerDiscoveryService(storage, llm)
    with patch("os.listdir", return_value=["a.md"]):
        storage.read_file.return_value = "Content"
        llm.generate.return_value = '["AAPL"]'
        assert "AAPL" in svc.discover_tickers_from_wiki()

        # Empty content
        storage.read_file.return_value = ""
        with patch("os.listdir", return_value=[]):
            assert svc.discover_tickers_from_wiki() == []

        # Exception
        storage.read_file.side_effect = Exception("Fail")
        assert svc.discover_tickers_from_wiki() == []


def test_discovery_volatile():
    storage = MagicMock()
    llm = MagicMock()
    svc = TickerDiscoveryService(storage, llm)
    with patch("os.listdir", return_value=["a.md"]):
        storage.read_file.return_value = "C"
        llm.generate.return_value = '["GME"]'
        assert "GME" in svc.discover_volatile_tickers()

        storage.read_file.side_effect = Exception("Fail")
        assert svc.discover_volatile_tickers() == []


def test_discovery_universe_mgmt():
    storage = MagicMock()
    llm = MagicMock()
    svc = TickerDiscoveryService(storage, llm)
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", MagicMock()),
        patch("json.load", side_effect=[["D"], ["P"]]),
        patch("json.dump"),
    ):
        res = svc.manage_universe({"P": "UPWARD", "D": "DOWNWARD"})
        assert "P" in res["promoted"]
        assert "D" in res["demoted"]

    with patch("os.path.exists", side_effect=Exception("Fail")):
        assert svc.manage_universe({}) == {"promoted": [], "demoted": []}


def test_discovery_update_universe():
    storage = MagicMock()
    llm = MagicMock()
    svc = TickerDiscoveryService(storage, llm)
    with (
        patch("os.path.exists", return_value=True),
        patch("builtins.open", MagicMock()),
        patch("json.load", return_value=["A"]),
        patch("json.dump"),
    ):
        svc.update_universe(["B"])

    with patch("os.path.exists", side_effect=Exception("Fail")):
        svc.update_universe(["C"])


def test_health_check():
    llm = MagicMock()
    svc = TickerDiscoveryService(MagicMock(), llm)
    llm.generate.return_value = '{"gaps":[], "missing_links":[], "suggestions":[]}'
    assert svc.run_wiki_health_check() is not None

    llm.generate.side_effect = Exception("Fail")
    assert svc.run_wiki_health_check() is None


def test_wiki_maintenance():
    storage = MagicMock()
    llm = MagicMock()
    svc = WikiMaintenanceService(storage, llm)
    storage.read_index.return_value = "Index"
    storage.list_unprocessed_research.return_value = ["f.txt"]
    storage._load_manifest.return_value = []
    storage.read_file.return_value = "C"

    # Success
    llm.generate.side_effect = ['{"title":"T","summary":"S","content":"C"}', "New Index"]
    assert svc.run_karpathy_loop().status == "completed"

    # Empty
    storage.list_unprocessed_research.return_value = []
    assert svc.run_karpathy_loop().status == "no_files"

    # Outer Exception
    storage.list_unprocessed_research.side_effect = Exception("Fail")
    assert svc.run_karpathy_loop().status == "failed"

    # Inner JSON Exception
    storage.list_unprocessed_research.side_effect = None
    storage.list_unprocessed_research.return_value = ["f.txt"]
    llm.generate.side_effect = ["Not JSON"]
    assert svc.run_karpathy_loop().status == "completed"  # Continues loop
