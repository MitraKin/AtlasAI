"""API endpoint tests using FastAPI TestClient."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "CityPulse API"
    assert "version" in data


@pytest.mark.asyncio
async def test_recommend_endpoint_infrastructure(client):
    payload = {
        "question": "We have ₹50L for infrastructure this quarter — where should it go?",
        "strategy": "balanced",
        "max_results": 3,
    }
    response = await client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "recommendations" in data
    assert "reasoning_trace" in data
    assert "metadata" in data

    assert len(data["recommendations"]) <= 3
    assert len(data["reasoning_trace"]) == 3
    assert data["metadata"]["total_duration_ms"] >= 0
    assert data["metadata"]["zones_analyzed"] > 0

    for rec in data["recommendations"]:
        assert "zone_id" in rec
        assert "zone_name" in rec
        assert "composite_score" in rec
        assert 0 <= rec["composite_score"] <= 100
        assert "confidence" in rec
        assert "justification" in rec
        assert "scores" in rec
        assert len(rec["scores"]) == 7


@pytest.mark.asyncio
async def test_recommend_endpoint_safety(client):
    payload = {
        "question": "Which zones need the most safety investment?",
        "strategy": "safety_first",
        "max_results": 5,
    }
    response = await client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) <= 5
    assert data["metadata"]["strategy"] == "safety_first"


@pytest.mark.asyncio
async def test_recommend_endpoint_sanitation(client):
    payload = {
        "question": "Where are sanitation problems worst?",
        "strategy": "equity_focused",
        "max_results": 3,
    }
    response = await client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) <= 3


@pytest.mark.asyncio
async def test_recommend_validates_input(client):
    response = await client.post("/api/v1/recommend", json={"question": "ab", "strategy": "balanced"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint(client):
    payload = {"question": "Why is my zone ranked lower?"}
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "citations" in data


@pytest.mark.asyncio
async def test_chat_specific_question(client):
    payload = {"question": "Tell me about the equity and fairness checks"}
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "equity" in data["answer"].lower()


@pytest.mark.asyncio
async def test_zones_list(client):
    response = await client.get("/api/v1/zones")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        z = data[0]
        assert "zone_id" in z
        assert "zone_name" in z
        assert "population" in z
        assert "complaint_count" in z


@pytest.mark.asyncio
async def test_zone_detail(client):
    response = await client.get("/api/v1/zones/Z01")
    assert response.status_code == 200
    data = response.json()
    assert data["zone_id"] == "Z01"
    assert data["zone_name"] == "Downtown Core"
    assert "population" in data
    assert "complaint_stats" in data
    assert "budget_history" in data
    assert "infrastructure" in data


@pytest.mark.asyncio
async def test_zone_not_found(client):
    response = await client.get("/api/v1/zones/Z99")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_scenarios_endpoint(client):
    payload = {
        "question": "re-rank with custom weights",
        "weights": {
            "complaint_volume": 0.10, "severity_index": 0.30, "accident_rate": 0.30,
            "cost_efficiency": 0.05, "population_impact": 0.10, "forecast_trend": 0.10, "equity_factor": 0.05,
        },
    }
    response = await client.post("/api/v1/scenarios", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0
    assert data["metadata"]["strategy"] == "custom"


@pytest.mark.asyncio
async def test_recommend_reasoning_steps_have_artifacts(client):
    payload = {"question": "Where should ₹50L go for road repairs?", "strategy": "balanced", "max_results": 1}
    response = await client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()

    for step in data["reasoning_trace"]:
        assert "agent" in step
        assert "step" in step
        assert "detail" in step
        assert "duration_ms" in step


@pytest.mark.asyncio
async def test_recommend_confidence_in_range(client):
    payload = {"question": "Show me the most underserved zones", "strategy": "equity_focused", "max_results": 3}
    response = await client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    for rec in data["recommendations"]:
        assert 0 <= rec["confidence"] <= 1


@pytest.mark.asyncio
async def test_all_strategies_via_api(client):
    for strategy in ["balanced", "safety_first", "cost_optimized", "equity_focused"]:
        payload = {"question": "Allocate infrastructure budget", "strategy": strategy, "max_results": 2}
        response = await client.post("/api/v1/recommend", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["strategy"] == strategy
