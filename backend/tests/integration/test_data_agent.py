"""Integration tests for the Data Agent."""

from app.repositories.data_repository import DataRepository
from app.agents.data_agent import run_data_agent, _extract_budget


class TestExtractBudget:
    def test_lakh(self):
        assert _extract_budget("We have ₹50L for infrastructure") == 5000000
        assert _extract_budget("Budget is 25 lakh") == 2500000

    def test_crore(self):
        assert _extract_budget("We have ₹2Cr allocated") == 20000000
        assert _extract_budget("Budget of 1 crore") == 10000000

    def test_no_budget(self):
        assert _extract_budget("Show me the best zones") is None

    def test_with_commas(self):
        result = _extract_budget("We have ₹1,50,000 for roads")
        assert result == 150000


class TestRunDataAgent:
    def test_returns_structured_result(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_data_agent("Where should infrastructure funding go?", repo)

        assert result["agent"] == "data_agent"
        assert "data" in result
        assert result["artifacts"] is not None
        assert "sql_generated" in result["artifacts"]
        assert "data_category" in result["artifacts"]
        assert result["duration_ms"] >= 0

    def test_attaches_zone_names(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_data_agent("Infrastructure budget", repo)

        for row in result["data"]:
            assert "zone_name" in row
            assert row["zone_name"]

    def test_different_categories(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)

        infra = run_data_agent("infrastructure planning", repo)
        safety = run_data_agent("traffic safety", repo)

        assert infra["category"] != safety["category"]

    def test_extracts_budget(self, temp_data_dir):
        repo = DataRepository(temp_data_dir)
        result = run_data_agent("We have ₹50L for roads", repo)
        assert result["budget"] == 5000000
