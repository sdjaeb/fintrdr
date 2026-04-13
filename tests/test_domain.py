from datetime import datetime

from src.domain.portfolio import Portfolio
from src.domain.research import ResearchDocument, WikiArticle, WikiIndex
from src.domain.risk import RiskAssessment, RiskProfile
from src.domain.strategy import InvestmentStrategy, TradingRule
from src.domain.telemetry import LearningSummary, MLModelMetrics, WikiLoopTelemetry


# --- Portfolio Tests ---
def test_portfolio_initialization():
    p = Portfolio(name="Test")
    assert p.name == "Test"
    assert p.cash == 100.0
    assert p.holdings == {}
    assert p.history == []


def test_portfolio_buy_success():
    p = Portfolio(name="Test")
    success = p.buy("AAPL", 0.5, 100.0, "Rationale")
    assert success is True
    assert p.cash == 50.0
    assert p.holdings["AAPL"] == 0.5
    assert len(p.history) == 1
    assert p.history[0].type == "BUY"


def test_portfolio_buy_insufficient_funds():
    p = Portfolio(name="Test")
    success = p.buy("AAPL", 2.0, 100.0)
    assert success is False
    assert p.cash == 100.0


def test_portfolio_sell_success():
    p = Portfolio(name="Test")
    p.buy("AAPL", 1.0, 50.0)
    success = p.sell("AAPL", 1.0, 100.0)  # Full sell
    assert success is True
    assert p.cash == 150.0
    assert "AAPL" not in p.holdings


def test_portfolio_sell_insufficient_holdings():
    p = Portfolio(name="Test")
    success = p.sell("AAPL", 1.0, 100.0)
    assert success is False


def test_portfolio_short_success():
    p = Portfolio(name="Test")
    success = p.short("TSLA", 1.0, 200.0)
    assert success is True
    assert p.cash == 300.0
    assert p.short_positions["TSLA"] == 1.0


def test_portfolio_cover_success():
    p = Portfolio(name="Test")
    p.short("TSLA", 1.0, 200.0)  # Cash = 300
    success = p.cover("TSLA", 1.0, 100.0)  # Full cover
    assert success is True
    assert p.cash == 200.0
    assert "TSLA" not in p.short_positions


def test_portfolio_cover_insufficient_short():
    p = Portfolio(name="Test")
    success = p.cover("TSLA", 1.0, 100.0)
    assert success is False


def test_portfolio_cover_insufficient_cash():
    p = Portfolio(name="Test")
    p.short("TSLA", 1.0, 100.0)  # Cash = 200
    success = p.cover("TSLA", 1.0, 300.0)  # Costs 300
    assert success is False


def test_portfolio_get_value():
    p = Portfolio(name="Test")
    p.buy("AAPL", 1.0, 100.0)  # Cash = 0, Holdings = 1 AAPL
    p.short("TSLA", 1.0, 200.0)  # Cash = 200, Shorts = 1 TSLA
    prices = {"AAPL": 150.0, "TSLA": 250.0}
    # Value = 200 (cash) + 150 (AAPL) - 250 (TSLA liability) = 100
    assert p.get_value(prices) == 100.0


# --- Research Domain Tests ---
def test_research_document():
    doc = ResearchDocument(source_url="url", title="Title", raw_content="Content")
    assert doc.title == "Title"


def test_wiki_article():
    article = WikiArticle(title="T", summary="S", content="C")
    assert article.title == "T"


def test_wiki_index():
    idx = WikiIndex(entities=["A", "B"])
    assert len(idx.entities) == 2


# --- Risk Domain Tests ---
def test_risk_profile():
    profile = RiskProfile(max_position_size_pct=0.2)
    assert profile.max_position_size_pct == 0.2


def test_risk_assessment():
    ass = RiskAssessment(symbol="AAPL", is_approved=True, recommended_quantity=1.0)
    assert ass.is_approved is True


# --- Strategy Domain Tests ---
def test_strategy_and_rules():
    rule = TradingRule(condition="C", action="A", params={"p": 1}, timing="IMMEDIATE")
    strat = InvestmentStrategy(name="S", description="D", target_tickers=["T"], rules=[rule], agent_source="Agent")
    assert strat.name == "S"
    assert strat.rules[0].timing == "IMMEDIATE"


# --- Telemetry Domain Tests ---
def test_wiki_telemetry_duration():
    t = WikiLoopTelemetry(iteration_id="id", start_time=datetime(2020, 1, 1, 12, 0, 0))
    assert t.duration_seconds == 0.0
    t.end_time = datetime(2020, 1, 1, 12, 0, 10)
    assert t.duration_seconds == 10.0


def test_ml_metrics():
    m = MLModelMetrics(
        total_samples_analyzed=10,
        mean_slope=0.1,
        volatility_index=0.2,
        prediction_confidence_score=0.8,
        last_update_duration_ms=100.0,
    )
    assert m.total_samples_analyzed == 10


def test_learning_summary():
    m = MLModelMetrics(
        total_samples_analyzed=10,
        mean_slope=0.1,
        volatility_index=0.2,
        prediction_confidence_score=0.8,
        last_update_duration_ms=100.0,
    )
    summary = LearningSummary(
        ml_metrics=m, top_momentum_tickers=["A"], bottom_momentum_tickers=["B"], system_evolution_notes="Notes"
    )
    assert summary.top_momentum_tickers[0] == "A"
