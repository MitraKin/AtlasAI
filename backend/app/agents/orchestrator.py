"""ADK Orchestrator — chains Data → Reasoning → Policy agents sequentially."""

import time
import logging

from app.repositories.data_repository import DataRepository
from app.agents.data_agent import run_data_agent
from app.agents.reasoning_agent import run_reasoning_agent
from app.agents.policy_agent import run_policy_agent

logger = logging.getLogger(__name__)


def run_pipeline(question: str, repo: DataRepository, strategy: str = "balanced") -> dict:
    total_start = time.time()
    reasoning_trace = []

    # Step 1: Data Agent
    data_result = run_data_agent(question, repo)
    reasoning_trace.append({
        "agent": data_result["agent"],
        "step": data_result["step"],
        "detail": data_result["detail"],
        "artifacts": data_result.get("artifacts"),
        "duration_ms": data_result["duration_ms"],
    })

    # Step 2: Reasoning Agent
    reasoning_result = run_reasoning_agent(data_result, strategy)
    reasoning_trace.append({
        "agent": reasoning_result["agent"],
        "step": reasoning_result["step"],
        "detail": reasoning_result["detail"],
        "artifacts": reasoning_result.get("artifacts"),
        "duration_ms": reasoning_result["duration_ms"],
    })

    # Step 3: Policy Agent
    policy_result = run_policy_agent(
        reasoning_result,
        data_result.get("budget"),
        strategy,
    )
    reasoning_trace.append({
        "agent": policy_result["agent"],
        "step": policy_result["step"],
        "detail": policy_result["detail"],
        "artifacts": policy_result.get("artifacts"),
        "duration_ms": policy_result["duration_ms"],
    })

    total_duration = int((time.time() - total_start) * 1000)
    rankings = policy_result.get("rankings", [])

    return {
        "recommendations": rankings,
        "reasoning_trace": reasoning_trace,
        "total_duration_ms": total_duration,
        "zones_analyzed": len(rankings),
    }
