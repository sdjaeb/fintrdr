import json
import os
from datetime import datetime


class Portfolio:
    """
    Manages virtual holdings, cash balance, and performance tracking.
    """

    def __init__(self, name: str, initial_cash: float = 100.0):
        self.name = name
        self.cash = initial_cash
        self.holdings: dict[str, float] = {}  # {symbol: quantity}
        self.history: list[dict] = []  # List of trade logs
        self.created_at = datetime.now().isoformat()

    def buy(self, symbol: str, quantity: float, price: float):
        total_cost = quantity * price
        if total_cost > self.cash:
            print(f"[{self.name}] Insufficient cash for {symbol}")
            return False

        self.cash -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.history.append(
            {
                "type": "BUY",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return True

    def sell(self, symbol: str, quantity: float, price: float):
        if self.holdings.get(symbol, 0) < quantity:
            print(f"[{self.name}] Insufficient shares of {symbol}")
            return False

        self.cash += quantity * price
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]

        self.history.append(
            {
                "type": "SELL",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "timestamp": datetime.now().isoformat(),
            }
        )
        return True

    def get_value(self, current_prices: dict[str, float]) -> float:
        holdings_value = sum(qty * current_prices.get(sym, 0) for sym, qty in self.holdings.items())
        return self.cash + holdings_value

    def save(self, directory: str = "src/simulator/portfolios"):
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"{self.name.lower().replace(' ', '_')}.json")
        with open(filepath, "w") as f:
            json.dump(self.__dict__, f, indent=4)
        return filepath
