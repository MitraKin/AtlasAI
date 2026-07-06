"""Integration tests for the full orchestrator pipeline."""

from app.agents.orchestrator import run_pipeline
from app.repositories.data_repository import DataRepository


class TestRunPipeline:
    def test_infrastructure_question(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_pipeline("We have ₹50L for infrastructure — where should it go?", repo, "balanced")

        assert "recommendations" in result
        assert "reasoning_trace" in result
        assert result["total_duration_ms"] >= 0
        assert len(result["reasoning_trace"]) == 3

    def test_reasoning_trace_order(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_pipeline("Show me infrastructure priorities", repo, "balanced")

        agents = [s["agent"] for s in result["reasoning_trace"]]
        assert agents == ["data_agent", "reasoning_agent", "policy_agent"]

    def test_safety_question(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_pipeline("Which zones have the worst safety record?", repo, "safety_first")

        assert result["zones_analyzed"] > 0

    def test_recommendations_have_required_fields(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_pipeline("Budget allocation for infrastructure", repo, "balanced")

        for rec in result["recommendations"]:
            assert "rank" in rec
            assert "zone_id" in rec
            assert "composite_score" in rec
            assert "confidence" in rec
            assert "justification" in rec
            assert "scores" in rec
            assert "bias_flags" in rec
            assert "data_citations" in rec

    def test_reasoning_steps_have_duration(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_pipeline("Where should we invest?", repo, "balanced")

        for step in result["reasoning_trace"]:
            assert step["duration_ms"] >= 0
            assert step["agent"] in ["data_agent", "reasoning_agent", "policy_agent"]
            assert len(step["detail"]) > 0

    def test_all_strategies_work(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        for strategy in ["balanced", "safety_first", "cost_optimized", "equity_focused"]:
            result = run_pipeline("Allocate budget for road repairs", repo, strategy)
            assert len(result["recommendations"]) > 0
