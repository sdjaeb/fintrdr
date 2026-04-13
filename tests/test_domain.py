from src.domain.portfolio import Portfolio
from src.domain.research import ResearchDocument, WikiArticle


def test_portfolio_buy_success():
    p = Portfolio(name="Test")
    assert p.cash == 100.0

    success = p.buy("AAPL", 0.5, 100.0)
    assert success is True
    assert p.cash == 50.0
    assert p.holdings["AAPL"] == 0.5
    assert len(p.history) == 1
    assert p.history[0].type == "BUY"


def test_portfolio_buy_insufficient_funds():
    p = Portfolio(name="Test")
    success = p.buy("AAPL", 2.0, 100.0)  # costs 200, only have 100
    assert success is False
    assert p.cash == 100.0
    assert len(p.holdings) == 0


def test_portfolio_sell_success():
    p = Portfolio(name="Test")
    p.buy("AAPL", 1.0, 50.0)  # cash down to 50

    success = p.sell("AAPL", 0.5, 100.0)  # sell half for 50
    assert success is True
    assert p.cash == 100.0
    assert p.holdings["AAPL"] == 0.5


def test_portfolio_sell_insufficient_holdings():
    p = Portfolio(name="Test")
    success = p.sell("AAPL", 1.0, 100.0)
    assert success is False


def test_portfolio_get_value():
    p = Portfolio(name="Test")
    p.buy("AAPL", 0.5, 100.0)  # cash 50, holdings AAPL 0.5

    prices = {"AAPL": 200.0}  # now worth 100
    assert p.get_value(prices) == 150.0  # 50 cash + 100 holdings


def test_research_document_creation():
    doc = ResearchDocument(source_url="http://test.com", title="Test", raw_content="Hello")
    assert doc.title == "Test"
    assert doc.raw_content == "Hello"


def test_wiki_article_creation():
    article = WikiArticle(title="Test", summary="Sum", content="Content", sources=["http://test.com"])
    assert article.title == "Test"
    assert len(article.sources) == 1
