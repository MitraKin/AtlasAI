"""Dependency injection for CityPulse."""

from app.config import get_settings
from app.repositories.data_repository import DataRepository
from app.services.recommendation import RecommendationService

_repo: DataRepository | None = None
_svc: RecommendationService | None = None


def get_repo() -> DataRepository:
    global _repo
    if _repo is None:
        settings = get_settings()
        _repo = DataRepository(settings.data_dir)
    return _repo


def get_recommendation_service() -> RecommendationService:
    global _svc
    if _svc is None:
        _svc = RecommendationService(get_repo())
    return _svc
