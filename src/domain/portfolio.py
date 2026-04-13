from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Trade(BaseModel):
    """
    Represents a single trade action.
    """

    type: Literal["BUY", "SELL", "SHORT", "COVER", "OPTION_BUY", "OPTION_SELL"]
    symbol: str
    quantity: float  # Supports fractional shares
    price: float
    timestamp: datetime = Field(default_factory=datetime.now)
    rationale: str | None = None


class Portfolio(BaseModel):
    """
    Manages virtual holdings, cash balance, and trade history.
    """

    name: str
    cash: float = 100.0
    holdings: dict[str, float] = Field(default_factory=dict)
    short_positions: dict[str, float] = Field(default_factory=dict)  # Track shorts separately
    history: list[Trade] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)

    def buy(self, symbol: str, quantity: float, price: float, rationale: str | None = None) -> bool:
        total_cost = quantity * price
        if total_cost > self.cash:
            return False

        self.cash -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0.0) + quantity
        self.history.append(Trade(type="BUY", symbol=symbol, quantity=quantity, price=price, rationale=rationale))
        return True

    def sell(self, symbol: str, quantity: float, price: float, rationale: str | None = None) -> bool:
        if self.holdings.get(symbol, 0.0) < quantity:
            return False

        self.cash += quantity * price
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] <= 0.0:
            del self.holdings[symbol]

        self.history.append(Trade(type="SELL", symbol=symbol, quantity=quantity, price=price, rationale=rationale))
        return True

    def short(self, symbol: str, quantity: float, price: float, rationale: str | None = None) -> bool:
        """
        Sells borrowed shares. Cash increases, but we owe the shares.
        """
        proceeds = quantity * price
        self.cash += proceeds
        self.short_positions[symbol] = self.short_positions.get(symbol, 0.0) + quantity
        self.history.append(Trade(type="SHORT", symbol=symbol, quantity=quantity, price=price, rationale=rationale))
        return True

    def cover(self, symbol: str, quantity: float, price: float, rationale: str | None = None) -> bool:
        """
        Buys back borrowed shares to close a short.
        """
        if self.short_positions.get(symbol, 0.0) < quantity:
            return False

        cost = quantity * price
        if cost > self.cash:
            return False

        self.cash -= cost
        self.short_positions[symbol] -= quantity
        if self.short_positions[symbol] <= 0.0:
            del self.short_positions[symbol]

        self.history.append(Trade(type="COVER", symbol=symbol, quantity=quantity, price=price, rationale=rationale))
        return True

    def get_value(self, current_prices: dict[str, float]) -> float:
        holdings_value = sum(qty * current_prices.get(sym, 0.0) for sym, qty in self.holdings.items())
        # Shorts reduce portfolio value as price goes up
        short_liability = sum(qty * current_prices.get(sym, 0.0) for sym, qty in self.short_positions.items())
        return self.cash + holdings_value - short_liability
