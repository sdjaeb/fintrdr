from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WikiLoopTelemetry(BaseModel):
    """
    Tracks performance and resource usage of a Karpathy Wiki Loop iteration.
    """

    iteration_id: str
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: datetime | None = None
    files_processed: int = 0
    tokens_estimated: int = 0
    ollama_response_time_ms: float = 0.0
    status: str = "started"
    error_message: str | None = None

    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class MLModelMetrics(BaseModel):
    """
    Tracks the health and predictive performance of our lightweight ML models.
    """

    model_name: str = "LinearTrajectoryRegressor"
    iteration_date: datetime = Field(default_factory=datetime.now)
    total_samples_analyzed: int
    mean_slope: float
    volatility_index: float  # Avg variance in analyzed prices
    prediction_confidence_score: float  # 0.0 to 1.0 based on R-squared avg
    last_update_duration_ms: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class LearningSummary(BaseModel):
    """
    Rollup of the system's progressive learning state.
    """

    date: datetime = Field(default_factory=datetime.now)
    ml_metrics: MLModelMetrics
    top_momentum_tickers: list[str]
    bottom_momentum_tickers: list[str]
    system_evolution_notes: str  # High-level summary of what the LLM learned from audits
