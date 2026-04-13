from typing import Any

import pandas as pd
import structlog
import yfinance as yf

from src.domain.portfolio import Portfolio
from src.domain.strategy import InvestmentStrategy, TradingRule

logger = structlog.get_logger()


class HistoricalSimulator:
    """
    Drives virtual portfolios using historical market data.
    """

    def __init__(self, tickers: list[str], start_date: str, end_date: str):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.data: pd.DataFrame = pd.DataFrame()
        self.portfolios: list[Portfolio] = []

    def load_data(self) -> bool:
        """
        Fetches historical data for all tickers in the specified period.
        """
        logger.info(
            "Fetching historical data",
            tickers=self.tickers,
            start=self.start_date,
            end=self.end_date,
        )
        try:
            # interval='1d' is standard for daily closing prices
            self.data = yf.download(self.tickers, start=self.start_date, end=self.end_date, interval="1d")["Close"]
            if self.data.empty:
                logger.error("No data found for these tickers in the given range.")
                return False
            # If multiple tickers, ensure 'Close' column names are correctly indexed
            if isinstance(self.data, pd.Series):
                self.data = self.data.to_frame()
                self.data.columns = [self.tickers[0]]
            return True
        except Exception as e:
            logger.error("Failed to download data", error=str(e))
            return False

    def run_strategy(self, portfolio: Portfolio, strategy: InvestmentStrategy):
        """
        Executes an agent-formulated InvestmentStrategy against historical data.
        """
        if self.data.empty:
            logger.error("Simulator data is empty. Run load_data() first.")
            return

        logger.info("Running Agent Strategy", portfolio=portfolio.name, strategy=strategy.name)

        for date, row in self.data.iterrows():
            prices = row.to_dict()
            for rule in strategy.rules:
                self._execute_rule(date, prices, portfolio, rule)

        final_prices = self.data.iloc[-1].to_dict()
        logger.info(
            "Simulation complete",
            portfolio=portfolio.name,
            final_value=portfolio.get_value(final_prices),
        )

    def _execute_rule(self, date: Any, prices: dict[str, float], portfolio: Portfolio, rule: TradingRule):
        """
        Interprets and executes a single TradingRule.
        """
        # For this prototype, we'll support simple conditions like 'price < X' or 'first_day'
        # In a production version, we'd use a more robust parser or safe eval.
        condition = rule.condition.lower()
        symbol = rule.params.get("symbol")

        if condition == "first_day" and date == self.data.index[0]:
            if symbol and symbol in prices:
                qty = portfolio.cash / prices[symbol]
                portfolio.buy(symbol, qty, prices[symbol], rationale=rule.action)

        elif "price <" in condition and symbol and symbol in prices:
            threshold = float(condition.split("<")[-1].strip())
            if prices[symbol] < threshold:
                # Simple buy logic: Use 50% of available cash
                qty = (portfolio.cash * 0.5) / prices[symbol]
                portfolio.buy(symbol, qty, prices[symbol], rationale=rule.action)

    def run_simulation(self, portfolio: Portfolio, strategy_func: Any):
        """
        Deprecated. Use run_strategy for Agent-based models.
        """
        if self.data.empty:
            logger.error("Simulator data is empty. Run load_data() first.")
            return

        logger.info("Starting legacy simulation run", portfolio=portfolio.name)

        for date, row in self.data.iterrows():
            prices = row.to_dict()
            strategy_func(date, prices, portfolio)

        final_value = portfolio.get_value(self.data.iloc[-1].to_dict())
        logger.info("Simulation complete", portfolio=portfolio.name, final_value=final_value)


if __name__ == "__main__":
    # Test simulation for 1997-1998 period
    sim = HistoricalSimulator(tickers=["AAPL", "MSFT", "INTC"], start_date="1997-05-01", end_date="1998-04-30")
    if sim.load_data():
        p = Portfolio(name="1997-Tech-Bet", cash=100.0)

        # A simple "Buy and Hold" strategy callback
        def buy_and_hold(date, prices, portfolio):
            if date == sim.data.index[0]:  # Buy on the first day
                portfolio.buy("AAPL", 0.5, prices["AAPL"], rationale="Initial buy")
                portfolio.buy("MSFT", 0.1, prices["MSFT"], rationale="Initial buy")

        sim.run_simulation(p, buy_and_hold)
        print(f"Final Value of 1997-Tech-Bet: ${p.get_value(sim.data.iloc[-1].to_dict()):.2f}")
