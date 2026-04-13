from typing import Any

import numpy as np
import structlog
from sklearn.linear_model import LinearRegression

logger = structlog.get_logger()


class QuantSignalProcessor:
    """
    Calculates advanced Simons-style mathematical signals.
    """

    def calculate_z_score(self, prices: list[float]) -> float:
        """
        Simons Technique: Mean Reversion.
        Returns how many standard deviations the current price is from the mean.
        > +2.0 = Overbought (Sell/Short signal)
        < -2.0 = Oversold (Buy/Rebound signal)
        """
        if len(prices) < 20:
            return 0.0
        arr = np.array(prices)
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return 0.0
        return float((arr[-1] - mean) / std)

    def detect_regime(self, prices: list[float]) -> str:
        """
        Simons Technique: Hidden Markov Model (Proxy).
        Identifies the current 'Market State' based on volatility.
        """
        if len(prices) < 10:
            return "UNKNOWN"

        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * np.sqrt(252)  # Annualized vol

        if volatility > 0.40:
            return "HIGH_VOLATILITY (Chaos/Opportunity)"
        elif volatility < 0.15:
            return "LOW_VOLATILITY (Quiet/Stable)"
        else:
            return "NORMAL (Trending)"


class TrajectoryPredictor:
    """
    Uses lightweight ML (Linear Regression) to identify trajectories
    for tickers based on historical price data.
    """

    def __init__(self):
        self.model = LinearRegression()

    def predict_trend_details(self, prices: list[float]) -> dict[str, Any]:
        """
        Returns trend details including slope and R-squared confidence.
        """
        if len(prices) < 5:
            return {"trend": "STABLE", "slope": 0.0, "r2": 0.0}

        # Prepare data for sklearn
        y = np.array(prices).reshape(-1, 1)
        x_vals = np.arange(len(prices)).reshape(-1, 1)

        self.model.fit(x_vals, y)
        slope = float(self.model.coef_[0][0])
        r2 = float(self.model.score(x_vals, y))

        trend = "FLAT"
        if slope > 0.05:
            trend = "UPWARD"
        elif slope < -0.05:
            trend = "DOWNWARD"

        return {"trend": trend, "slope": slope, "r2": r2}

    def predict_trend(self, prices: list[float]) -> str:
        details = self.predict_trend_details(prices)
        return f"{details['trend']} (Slope: {details['slope']:.2f})"

    def get_growth_rate(self, prices: list[float]) -> float:
        """
        Calculates simple growth rate percentage.
        """
        if not prices:
            return 0.0
        return ((prices[-1] - prices[0]) / prices[0]) * 100
