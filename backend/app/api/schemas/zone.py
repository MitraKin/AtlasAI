from pydantic import BaseModel


class ZoneSummary(BaseModel):
    zone_id: str
    zone_name: str
    population: int
    area_sqkm: float
    median_income: int
    complaint_count: int
    avg_severity: float
    composite_score: float | None = None


class ZoneDetail(BaseModel):
    zone_id: str
    zone_name: str
    population: int
    area_sqkm: float
    median_income: int
    population_density: int
    poverty_rate: float
    complaint_stats: dict
    budget_history: list[dict]
    infrastructure: list[dict]
    forecast: dict | None = None
