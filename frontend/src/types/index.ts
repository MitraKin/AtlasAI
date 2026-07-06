export interface ScoreBreakdown {
  complaint_volume: number
  severity_index: number
  accident_rate: number
  cost_efficiency: number
  population_impact: number
  forecast_trend: number
  equity_factor: number
}

export interface ZoneRecommendation {
  rank: number
  zone_id: string
  zone_name: string
  composite_score: number
  confidence: number
  suggested_budget_allocation: number
  justification: string
  scores: ScoreBreakdown
  bias_flags: string[]
  data_citations: string[]
}

export interface ReasoningStep {
  agent: string
  step: string
  detail: string
  artifacts: Record<string, unknown> | null
  duration_ms: number
}

export interface ResponseMetadata {
  total_duration_ms: number
  zones_analyzed: number
  strategy: string
}

export interface RecommendResponse {
  recommendations: ZoneRecommendation[]
  reasoning_trace: ReasoningStep[]
  metadata: ResponseMetadata
}

export interface ZoneSummary {
  zone_id: string
  zone_name: string
  population: number
  area_sqkm: number
  median_income: number
  complaint_count: number
  avg_severity: number
  composite_score: number | null
}

export interface ChatMessage {
  question: string
  answer: string
}

export type Strategy = 'balanced' | 'safety_first' | 'cost_optimized' | 'equity_focused'
