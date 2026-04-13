from unittest.mock import patch

import pandas as pd

from src.application.backtest_service import ShadowBacktestService
from src.application.simulator_service import HistoricalSimulator
from src.domain.portfolio import Portfolio
from src.domain.strategy import InvestmentStrategy, TradingRule


def test_historical_simulator_load_data():
    sim = HistoricalSimulator(["AAPL", "MSFT"], "2020-01-01", "2020-01-10")

    # 1. Multi ticker success
    df = pd.DataFrame({("Close", "AAPL"): [100.0], ("Close", "MSFT"): [200.0]}, index=pd.to_datetime(["2020-01-01"]))
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    with patch("yfinance.download", return_value=df):
        assert sim.load_data() is True

    # 2. Single ticker success
    sim_single = HistoricalSimulator(["AAPL"], "2020-01-01", "2020-01-10")
    df_single = pd.DataFrame({"Close": [100.0]}, index=pd.to_datetime(["2020-01-01"]))
    with patch("yfinance.download", return_value=df_single):
        assert sim_single.load_data() is True

    # 3. Fail (Empty)
    with patch("yfinance.download", return_value=pd.DataFrame()):
        assert sim_single.load_data() is False

    # 4. Fail (Exception)
    with patch("yfinance.download", side_effect=Exception("Fail")):
        assert sim_single.load_data() is False


def test_historical_simulator_run_strategy():
    sim = HistoricalSimulator(["AAPL"], "2020-01-01", "2020-01-10")
    sim.data = pd.DataFrame({"AAPL": [100, 110, 90]}, index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]))

    p = Portfolio(name="P")
    strat = InvestmentStrategy(
        name="S",
        description="D",
        target_tickers=["AAPL"],
        rules=[
            TradingRule(condition="first_day", action="BUY", params={"symbol": "AAPL"}),
            TradingRule(condition="price < 95", action="BUY", params={"symbol": "AAPL"}),
        ],
        agent_source="A",
    )

    sim.run_strategy(p, strat)
    assert len(p.history) == 2

    # 4. Other rule conditions (for coverage)
    # price > X is not implemented but we can check if it doesn't crash or if we add it
    # Current implementation supports 'first_day' and 'price < X'

    # Empty run
    sim_empty = HistoricalSimulator(["X"], "2020-01-01", "2020-01-10")
    sim_empty.run_strategy(p, strat)  # Logs error


def test_historical_simulator_deprecated():
    sim = HistoricalSimulator(["AAPL"], "2020-01-01", "2020-01-10")
    sim.data = pd.DataFrame({"AAPL": [100]}, index=[pd.Timestamp("2020-01-01")])
    p = Portfolio(name="P")
    sim.run_simulation(p, lambda d, pr, po: po.buy("AAPL", 1, 100))
    assert len(p.history) == 1


def test_shadow_backtest_service():
    svc = ShadowBacktestService()
    with patch("src.application.simulator_service.HistoricalSimulator") as mock_sim:
        inst = mock_sim.return_value
        inst.load_data.return_value = True
        inst.data = pd.DataFrame({"AAPL": [100]}, index=[pd.Timestamp("2020-01-01")])
        res = svc.run_shadow_test("AAPL")
        assert res is not None

        inst.load_data.return_value = False
        assert svc.run_shadow_test("FAIL") is None
