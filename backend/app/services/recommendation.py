"""Recommendation service — wraps the orchestrator for API consumption."""

from app.agents.orchestrator import run_pipeline
from app.repositories.data_repository import DataRepository


class RecommendationService:
    def __init__(self, repo: DataRepository):
        self.repo = repo

    def get_recommendations(self, question: str, strategy: str = "balanced") -> dict:
        return run_pipeline(question, self.repo, strategy)
