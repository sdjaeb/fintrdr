import structlog

from src.domain.portfolio import Portfolio
from src.domain.risk import RiskAssessment, RiskProfile

logger = structlog.get_logger()


class RiskManager:
    """
    Enforces risk constraints on all proposed trades.
    """

    def __init__(self, profile: RiskProfile = RiskProfile()):
        self.profile = profile

    def determine_cash_reserve(self, trajectories: dict[str, str]) -> float:
        """
        Dynamically adjusts the required cash reserve based on overall market sentiment.
        """
        bearish_count = sum(1 for t in trajectories.values() if "DOWNWARD" in t)
        total_count = len(trajectories)

        if total_count == 0:
            return self.profile.emergency_cash_reserve_pct

        bear_ratio = bearish_count / total_count

        if bear_ratio > 0.5:
            logger.info("Market Sentiment: Bearish. Increasing cash protection.")
            return min(0.50, self.profile.emergency_cash_reserve_pct * 2.5)

        bullish_count = sum(1 for t in trajectories.values() if "UPWARD" in t)
        if total_count > 0 and bullish_count / total_count > 0.8:
            logger.info("Market Sentiment: Strongly Bullish. Maximizing deployment.")
            return 0.05

        return self.profile.emergency_cash_reserve_pct

    def validate_trade(
        self,
        portfolio: Portfolio,
        symbol: str,
        quantity: float,
        price: float,
        cash_reserve_pct: float | None = None,
    ) -> RiskAssessment:
        """
        Validates if a trade fits within the defined risk profile.
        """
        current_value = portfolio.get_value({symbol: price})
        trade_value = quantity * price
        reserve_pct = cash_reserve_pct if cash_reserve_pct is not None else self.profile.emergency_cash_reserve_pct

        # 1. Check Portfolio-wide Crypto Cap
        is_crypto = "-USD" in symbol or symbol in ["BTC", "ETH", "SOL"]
        if is_crypto:
            current_crypto_val = sum(qty * price for sym, qty in portfolio.holdings.items() if "-USD" in sym)
            if (current_crypto_val + trade_value) / current_value > self.profile.max_crypto_exposure_pct:
                logger.warn("Risk Violation: Crypto Cap Exceeded", symbol=symbol)
                allowed_val = (current_value * self.profile.max_crypto_exposure_pct) - current_crypto_val
                new_qty = max(0, allowed_val / price)
                return RiskAssessment(
                    symbol=symbol,
                    is_approved=True,
                    adjustment_reason="Capped by Crypto Exposure Limit",
                    recommended_quantity=new_qty,
                )

        # 2. Check Single Position Size Cap
        if current_value > 0 and trade_value / current_value > self.profile.max_position_size_pct:
            logger.warn("Risk Violation: Position Size Too Large", symbol=symbol)
            new_qty = (current_value * self.profile.max_position_size_pct) / price
            return RiskAssessment(
                symbol=symbol,
                is_approved=True,
                adjustment_reason="Capped by Position Size Limit",
                recommended_quantity=new_qty,
            )

        # 3. Check Cash Reserve
        if current_value > 0 and (portfolio.cash - trade_value) / current_value < reserve_pct:
            logger.warn("Risk Violation: Cash Reserve Low", symbol=symbol)
            allowed_cash = portfolio.cash - (current_value * reserve_pct)
            if allowed_cash <= 0:
                return RiskAssessment(symbol=symbol, is_approved=False, recommended_quantity=0)
            new_qty = allowed_cash / price
            return RiskAssessment(
                symbol=symbol,
                is_approved=True,
                adjustment_reason=f"Capped by {reserve_pct*100}% Cash Reserve",
                recommended_quantity=new_qty,
            )

        return RiskAssessment(symbol=symbol, is_approved=True, recommended_quantity=quantity)
