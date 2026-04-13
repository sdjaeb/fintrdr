from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TradingRule(BaseModel):
    """
    A specific condition and action (e.g., 'If RSI < 30, BUY').
    """

    condition: str
    action: str
    params: dict[str, Any] = Field(default_factory=dict)
    timing: str = "IMMEDIATE"


class InvestmentStrategy(BaseModel):
    """
    A high-level strategy formulated by the Strategy Agent.
    """

    name: str
    description: str
    target_tickers: list[str]
    rules: list[TradingRule]
    agent_source: str
    created_at: datetime = Field(default_factory=datetime.now)
    backtest_period: str | None = None  # e.g., '1997-2007'
    performance_metadata: dict[str, Any] = Field(default_factory=dict)
