"""Data Agent — translates NL questions into data queries using Gemini 2.0 Flash.

Falls back to keyword-based pattern matching when Gemini is unavailable.
"""

import time
import re
import logging

from app.repositories.data_repository import DataRepository
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

_gemini = GeminiService()


def _extract_budget(question: str) -> float | None:
    q = question.replace(",", "").replace("₹", "").replace("$", "")
    match = re.search(r"(\d+)\s*(?:lakh|lac|lk?|L)\b", q.lower())
    if match:
        return float(match.group(1)) * 100000
    match = re.search(r"(\d+)\s*(?:crore|cr|Cr)\b", q.lower())
    if match:
        return float(match.group(1)) * 10000000
    match = re.search(r"(\d+)\s*(?:k|thousand|000)\b", q.lower())
    if match:
        return float(match.group(1)) * 1000
    return None


def run_data_agent(question: str, repo: DataRepository) -> dict:
    start = time.time()
    budget = _extract_budget(question)

    gemini_result = _gemini.generate_sql(question)
    sql = gemini_result["sql"]
    category = gemini_result.get("category", "infrastructure")
    explanation = gemini_result.get("explanation", "")

    try:
        data = repo.execute_query(sql)
    except Exception as e:
        logger.error("data_agent_query_failed: %s", str(e))
        data = []

    name_map = repo.get_zone_name_map()
    for row in data:
        row["zone_name"] = name_map.get(row.get("zone_id", ""), row.get("zone_id", ""))

    duration_ms = int((time.time() - start) * 1000)

    return {
        "agent": "data_agent",
        "step": f"Querying {category} data across zones",
        "detail": explanation or f"Retrieved {len(data)} zones with {category} metrics from civic data records.",
        "artifacts": {
            "sql_generated": sql.strip()[:500],
            "data_category": category,
            "rows_retrieved": len(data),
            "nl_to_sql_method": "gemini" if _gemini.available else "keyword_pattern",
        },
        "duration_ms": duration_ms,
        "data": data,
        "budget": budget,
        "category": category,
    }
