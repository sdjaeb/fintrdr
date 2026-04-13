from pydantic import BaseModel


class RiskProfile(BaseModel):
    """
    Global risk constraints for the investment engine.
    """

    max_position_size_pct: float = 0.15  # Max 15% in any single ticker
    max_crypto_exposure_pct: float = 0.05  # Max 5% in total crypto (per user goal)
    stop_loss_pct: float = 0.07  # Sell if position drops 7%
    take_profit_pct: float = 0.50  # Consider rebalancing if up 50%
    emergency_cash_reserve_pct: float = 0.10  # Always keep 10% in cash


class RiskAssessment(BaseModel):
    """
    Assessment of a specific proposed trade.
    """

    symbol: str
    is_approved: bool
    adjustment_reason: str | None = None
    recommended_quantity: float
