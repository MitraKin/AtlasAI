from pydantic import BaseModel, Field
from .common import Strategy


class ScoreBreakdown(BaseModel):
    complaint_volume: float = Field(ge=0, le=100)
    severity_index: float = Field(ge=0, le=100)
    accident_rate: float = Field(ge=0, le=100)
    cost_efficiency: float = Field(ge=0, le=100)
    population_impact: float = Field(ge=0, le=100)
    forecast_trend: float = Field(ge=0, le=100)
    equity_factor: float = Field(ge=0, le=100)


class ZoneRecommendation(BaseModel):
    rank: int
    zone_id: str
    zone_name: str
    composite_score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    suggested_budget_allocation: float
    justification: str
    scores: ScoreBreakdown
    bias_flags: list[str] = []
    data_citations: list[str] = []


class ReasoningStep(BaseModel):
    agent: str
    step: str
    detail: str
    artifacts: dict | None = None
    duration_ms: int = 0


class ResponseMetadata(BaseModel):
    total_duration_ms: int
    zones_analyzed: int
    strategy: Strategy


class RecommendRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    budget: float | None = None
    period: str | None = None
    category: str | None = None
    zone_ids: list[str] | None = None
    strategy: Strategy = Strategy.BALANCED
    max_results: int = Field(default=10, ge=1, le=15)


class RecommendResponse(BaseModel):
    recommendations: list[ZoneRecommendation]
    reasoning_trace: list[ReasoningStep]
    metadata: ResponseMetadata


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    context: dict | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[str] = []


class ScenarioRequest(BaseModel):
    question: str
    base_recommendation_id: str | None = None
    weights: dict[str, float]
    max_results: int = Field(default=10, ge=1, le=15)


class ErrorResponse(BaseModel):
    error: str
    detail: str
    request_id: str | None = None
