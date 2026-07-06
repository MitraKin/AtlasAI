"""Gemini 2.0 Flash service — NL to SQL generation, chat, and fallback.

Used by the Data Agent for question→SQL translation and the Chat endpoint
for free-form follow-up Q&A with recommendation context.
"""

import json
import logging
import re

from app.config import get_settings

logger = logging.getLogger(__name__)

DB_SCHEMA = """
Tables available in SQLite (all column names are lowercase, underscores):

complaints_311(complaint_id, created_date, closed_date, category, subcategory,
  status, zone_id, latitude, longitude, severity, resolution_days, description)
-- severity 1-5, category values: 'infrastructure','safety','sanitation','water','trash','electricity'

traffic_incidents(incident_id, date, time, zone_id, latitude, longitude,
  severity, type, road_type, weather_condition, injuries, fatalities)

budget_historical(id, fiscal_year, quarter, zone_id, department, category,
  allocated_amount, spent_amount, project_count, completion_rate)

census_demographics(zone_id, population, population_growth_rate, median_income,
  poverty_rate, median_age, households, vehicle_ownership_pct, education_pct_college)

infrastructure_assets(id, zone_id, asset_type, avg_age_years,
  pct_past_lifecycle, last_major_repair, condition_score)
-- asset_type values: 'road','water_pipe','sewer','power_line','bridge','building'

utility_outages(outage_id, date, zone_id, type, duration_hours,
  affected_residents, cause, latitude, longitude)

zone_metadata(zone_id, zone_name, area_sqkm, population, median_income,
  population_density, geometry)

JOIN pattern: always LEFT JOIN other tables to complaints_311 ON zone_id.
Use zone_metadata.zone_name for labels. All zone_id are strings like 'Z01','Z02',...,'Z15'.
"""

SQL_SYSTEM_PROMPT = f"""You are a municipal data analyst generating SQL queries for a civic data warehouse.
Given a natural language question about city infrastructure, safety, budget, or demographics,
generate a single SQL SELECT query.

{DB_SCHEMA}

RULES:
1. Return ONLY a JSON object: {{"sql": "...", "category": "...", "explanation": "..."}}
2. Always SELECT all relevant numeric metrics + zone_metadata.zone_name with LEFT JOIN zone_metadata ON zone_id.
3. Always include metrics needed for scoring: complaint counts, severity, traffic incidents, budget spent %, population, poverty rate, infrastructure condition.
4. Always GROUP BY zone_id and ORDER BY a meaningful metric DESC.
5. Use MAX(CASE WHEN ...) for pivoting infrastructure_assets condition scores.
6. For budget amounts, interpret ₹/lakh (1 lakh = 100000), crore (1 crore = 10000000).
7. Category identifies the question domain: 'infrastructure', 'safety', 'sanitation', 'budget', 'demographics', 'transportation'.
8. Include equity_need as: CASE WHEN d.poverty_rate > 0.20 THEN 80 ELSE 50 END
9. For forecast_trend, default to 0.
10. Use COALESCE/IFNULL for nullable columns in LEFT JOINs.
11. Only output valid SQL that works on SQLite.
12. Do NOT wrap the JSON in markdown code blocks."""

CHAT_SYSTEM_PROMPT = """You are CityPulse, an AI civic decision copilot that helps municipal planners
allocate resources across city zones based on data-driven analysis.

You have access to civic data: 311 complaints, traffic incidents, budget history,
census demographics, infrastructure conditions, and utility outages across 15 zones.

When answering:
- Be concise and data-driven (2-4 sentences).
- Reference specific zone IDs (Z01-Z15) and metrics when relevant.
- If the user asks about methodology, explain the 3-agent pipeline: Data → Reasoning → Policy.
- If the user asks about scoring, mention the 7 weighted factors.
- If asked about strategies, explain: balanced, safety_first, cost_optimized, equity_focused.
- If asked something unrelated to civic planning, politely redirect."""


class GeminiService:
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self._client = None

    @property
    def client(self):
        if self._client is None and self.api_key:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    @property
    def available(self) -> bool:
        return bool(self.api_key and self.client)

    def generate_sql(self, question: str) -> dict:
        if not self.available:
            logger.warning("gemini_unavailable: falling back to keyword matching")
            return self._fallback_sql(question)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"Question: {question}\n\nGenerate the SQL query as JSON.",
                config={
                    "system_instruction": SQL_SYSTEM_PROMPT,
                    "temperature": 0.1,
                    "max_output_tokens": 2000,
                },
            )

            raw = response.text.strip()
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw).strip()
            result = json.loads(raw)

            if "sql" not in result:
                raise ValueError("Gemini response missing 'sql' field")

            logger.info("gemini_sql_generated: category=%s", result.get("category", "unknown"))
            return result

        except Exception as e:
            logger.error("gemini_sql_failed: %s, falling back to pattern matching", str(e))
            return self._fallback_sql(question)

    def chat(self, question: str, context: dict | None = None) -> dict:
        if not self.available:
            return self._fallback_chat(question)

        try:
            ctx_str = ""
            if context:
                ctx_str = f"\nCurrent context (recommendation results): {json.dumps(context, default=str)[:2000]}"

            response = self.client.models.generate_content(
                model=self.model,
                contents=f"User question: {question}{ctx_str}",
                config={
                    "system_instruction": CHAT_SYSTEM_PROMPT,
                    "temperature": 0.3,
                    "max_output_tokens": 1024,
                },
            )

            answer = response.text.strip()
            logger.info("gemini_chat_response: %d chars", len(answer))
            return {"answer": answer, "citations": self._extract_citations(answer)}

        except Exception as e:
            logger.error("gemini_chat_failed: %s", str(e))
            return self._fallback_chat(question)

    def _extract_citations(self, text: str) -> list[str]:
        citations = []
        if "complaint" in text.lower():
            citations.append("civic_raw.complaints_311")
        if "traffic" in text.lower():
            citations.append("civic_raw.traffic_incidents")
        if "budget" in text.lower():
            citations.append("civic_raw.budget_historical")
        if "demographic" in text.lower() or "census" in text.lower():
            citations.append("civic_raw.census_demographics")
        if "infrastructure" in text.lower() or "asset" in text.lower():
            citations.append("civic_raw.infrastructure_assets")
        return citations[:3] if citations else ["civic_raw.complaints_311"]

    def _fallback_sql(self, question: str) -> dict:
        q = question.lower()
        if any(w in q for w in ["safety", "accident", "traffic", "crash"]):
            category = "safety"
        elif any(w in q for w in ["sanitation", "trash", "sewer", "waste", "garbage"]):
            category = "sanitation"
        elif any(w in q for w in ["budget", "spending", "allocation", "fund"]):
            category = "budget"
        elif any(w in q for w in ["demographic", "population", "poverty", "income"]):
            category = "demographics"
        else:
            category = "infrastructure"

        return {
            "sql": _FALLBACK_SQL.get(category, _FALLBACK_SQL["infrastructure"]),
            "category": category,
            "explanation": f"Fallback: keyword matched to {category} pattern.",
        }

    def _fallback_chat(self, question: str) -> dict:
        q = question.lower()
        responses = {
            "why": "The ranking is based on a weighted multi-criteria scoring system that evaluates 7 factors: complaint volume, severity, accident rates, cost efficiency, population impact, forecast trends, and equity. Zones with higher scores in the most heavily weighted factors rank higher.",
            "how": "CityPulse uses a 3-agent pipeline: the Data Agent retrieves civic data, the Reasoning Agent applies weighted scoring, and the Policy Agent checks for bias and generates explanations.",
            "what": "The recommendations show which zones need the most investment based on data-driven analysis. Each recommendation includes a composite score, confidence level, suggested budget, and justification.",
            "safety": "When safety is prioritized, the scoring weights for severity index and accident rate are increased. This means zones with higher accident severity and more traffic incidents will rank higher.",
            "equity": "The equity factor boosts scores for zones with higher poverty rates and historically underfunded areas. You can enable the 'Equity Focused' strategy in the scenario simulator.",
            "budget": "Budget allocation is based on composite scores and the selected strategy. Top-ranked zones receive higher suggested allocations proportional to their score.",
        }
        for key, resp in responses.items():
            if key in q:
                return {"answer": resp, "citations": ["civic_raw.complaints_311"]}

        return {
            "answer": (
                "CityPulse analyzes civic data across zones to provide evidence-based recommendations. "
                "Each recommendation shows the reasoning behind it — what data was used, how scores were calculated, "
                "and any potential bias that was detected. Try asking 'where should infrastructure funding go?' "
                "or 'which zones need the most safety investment?'"
            ),
            "citations": ["civic_raw.complaints_311", "civic_features.zone_complaint_density"],
        }


_FALLBACK_SQL = {
    "infrastructure": """SELECT
    c.zone_id, zm.zone_name, c.total_complaints, c.avg_severity, c.pct_critical,
    c.avg_resolution_days, c.open_backlog,
    COALESCE(t.total_incidents, 0) as total_incidents,
    COALESCE(t.avg_severity, 0) as traffic_severity,
    COALESCE(b.pct_spent, 0) as pct_spent,
    COALESCE(b.avg_completion_rate, 0) as avg_completion_rate,
    d.population, d.median_income, d.poverty_rate, d.vehicle_ownership_pct,
    MAX(CASE WHEN i.asset_type = 'road' THEN i.condition_score END) as road_condition,
    MAX(CASE WHEN i.asset_type = 'water_pipe' THEN i.condition_score END) as water_condition,
    0 as forecast_trend,
    CASE WHEN d.poverty_rate > 0.20 THEN 80 ELSE 50 END as equity_need
FROM (SELECT zone_id, COUNT(*) as total_complaints,
    AVG(severity) as avg_severity,
    SUM(CASE WHEN severity >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as pct_critical,
    AVG(CASE WHEN resolution_days IS NOT NULL THEN resolution_days END) as avg_resolution_days,
    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_backlog
    FROM complaints_311 GROUP BY zone_id) c
LEFT JOIN (SELECT zone_id, COUNT(*) as total_incidents, AVG(severity) as avg_severity
    FROM traffic_incidents GROUP BY zone_id) t ON c.zone_id = t.zone_id
LEFT JOIN (SELECT zone_id,
    SUM(spent_amount) * 100.0 / NULLIF(SUM(allocated_amount), 0) as pct_spent,
    AVG(completion_rate) as avg_completion_rate
    FROM budget_historical GROUP BY zone_id) b ON c.zone_id = b.zone_id
LEFT JOIN census_demographics d ON c.zone_id = d.zone_id
LEFT JOIN infrastructure_assets i ON c.zone_id = i.zone_id
LEFT JOIN zone_metadata zm ON c.zone_id = zm.zone_id
GROUP BY c.zone_id ORDER BY c.total_complaints DESC""",

    "safety": """SELECT
    c.zone_id, zm.zone_name, c.total_complaints, c.avg_severity, c.pct_critical,
    c.avg_resolution_days, c.open_backlog,
    COALESCE(t.total_incidents, 0) as total_incidents,
    COALESCE(t.avg_severity, 0) as traffic_severity,
    COALESCE(t.total_fatalities, 0) as total_fatalities,
    COALESCE(b.pct_spent, 0) as pct_spent,
    COALESCE(b.avg_completion_rate, 0) as avg_completion_rate,
    d.population, d.median_income, d.poverty_rate,
    MAX(CASE WHEN i.asset_type = 'road' THEN i.condition_score END) as road_condition,
    0 as forecast_trend,
    CASE WHEN d.poverty_rate > 0.20 THEN 80 ELSE 50 END as equity_need
FROM (SELECT zone_id, COUNT(*) as total_complaints,
    AVG(severity) as avg_severity,
    SUM(CASE WHEN severity >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as pct_critical,
    AVG(CASE WHEN resolution_days IS NOT NULL THEN resolution_days END) as avg_resolution_days,
    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_backlog
    FROM complaints_311 GROUP BY zone_id) c
LEFT JOIN (SELECT zone_id, COUNT(*) as total_incidents, AVG(severity) as avg_severity,
    SUM(fatalities) as total_fatalities FROM traffic_incidents GROUP BY zone_id) t
    ON c.zone_id = t.zone_id
LEFT JOIN (SELECT zone_id,
    SUM(spent_amount) * 100.0 / NULLIF(SUM(allocated_amount), 0) as pct_spent,
    AVG(completion_rate) as avg_completion_rate
    FROM budget_historical GROUP BY zone_id) b ON c.zone_id = b.zone_id
LEFT JOIN census_demographics d ON c.zone_id = d.zone_id
LEFT JOIN infrastructure_assets i ON c.zone_id = i.zone_id
LEFT JOIN zone_metadata zm ON c.zone_id = zm.zone_id
GROUP BY c.zone_id ORDER BY COALESCE(t.total_incidents, 0) DESC""",

    "sanitation": """SELECT
    c.zone_id, zm.zone_name, c.total_complaints, c.avg_severity, c.pct_critical,
    c.avg_resolution_days, c.open_backlog,
    COALESCE(t.total_incidents, 0) as total_incidents,
    COALESCE(t.avg_severity, 0) as traffic_severity,
    COALESCE(b.pct_spent, 0) as pct_spent,
    COALESCE(b.avg_completion_rate, 0) as avg_completion_rate,
    d.population, d.median_income, d.poverty_rate,
    MAX(CASE WHEN i.asset_type = 'sewer' THEN i.condition_score END) as sewer_condition,
    0 as forecast_trend,
    CASE WHEN d.poverty_rate > 0.20 THEN 80 ELSE 50 END as equity_need
FROM (SELECT zone_id, COUNT(*) as total_complaints,
    AVG(severity) as avg_severity,
    SUM(CASE WHEN severity >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as pct_critical,
    AVG(CASE WHEN resolution_days IS NOT NULL THEN resolution_days END) as avg_resolution_days,
    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_backlog
    FROM complaints_311 WHERE category IN ('sanitation', 'trash', 'water')
    GROUP BY zone_id) c
LEFT JOIN (SELECT zone_id, COUNT(*) as total_incidents, AVG(severity) as avg_severity
    FROM traffic_incidents GROUP BY zone_id) t ON c.zone_id = t.zone_id
LEFT JOIN (SELECT zone_id,
    SUM(spent_amount) * 100.0 / NULLIF(SUM(allocated_amount), 0) as pct_spent,
    AVG(completion_rate) as avg_completion_rate
    FROM budget_historical WHERE category = 'sanitation' GROUP BY zone_id) b
    ON c.zone_id = b.zone_id
LEFT JOIN census_demographics d ON c.zone_id = d.zone_id
LEFT JOIN infrastructure_assets i ON c.zone_id = i.zone_id
LEFT JOIN zone_metadata zm ON c.zone_id = zm.zone_id
GROUP BY c.zone_id ORDER BY c.total_complaints DESC""",
}
