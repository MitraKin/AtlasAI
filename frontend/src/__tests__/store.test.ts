import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAppStore } from '../stores/app'
import type { RecommendResponse } from '../types'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

function mockRecommendResponse(overrides: Partial<RecommendResponse> = {}): RecommendResponse {
  return {
    recommendations: [
      {
        rank: 1, zone_id: 'Z01', zone_name: 'Downtown', composite_score: 85, confidence: 0.92,
        suggested_budget_allocation: 750000, justification: 'High complaints and severity',
        scores: { complaint_volume: 90, severity_index: 85, accident_rate: 80, cost_efficiency: 70, population_impact: 60, forecast_trend: 50, equity_factor: 40 },
        bias_flags: [], data_citations: [],
      },
      {
        rank: 2, zone_id: 'Z02', zone_name: 'Suburb', composite_score: 65, confidence: 0.88,
        suggested_budget_allocation: 750000, justification: 'Moderate scores',
        scores: { complaint_volume: 50, severity_index: 60, accident_rate: 40, cost_efficiency: 80, population_impact: 30, forecast_trend: 60, equity_factor: 70 },
        bias_flags: ['Equity factor is low'], data_citations: [],
      },
    ],
    reasoning_trace: [
      { agent: 'data_agent', step: 'Querying', detail: 'Found data', artifacts: null, duration_ms: 50 },
      { agent: 'reasoning_agent', step: 'Scoring', detail: 'Ranked zones', artifacts: null, duration_ms: 10 },
      { agent: 'policy_agent', step: 'Checking', detail: 'Equity check passed', artifacts: null, duration_ms: 5 },
    ],
    metadata: { total_duration_ms: 100, zones_analyzed: 15, strategy: 'balanced' },
    ...overrides,
  }
}

beforeEach(() => {
  mockFetch.mockReset()
  useAppStore.setState({
    question: '', strategy: 'balanced', response: null, loading: false, error: null, activeStep: 0,
  })
})

describe('useAppStore', () => {
  it('has initial state', () => {
    const state = useAppStore.getState()
    expect(state.question).toBe('')
    expect(state.strategy).toBe('balanced')
    expect(state.response).toBeNull()
    expect(state.loading).toBe(false)
    expect(state.error).toBeNull()
    expect(state.activeStep).toBe(0)
  })

  it('setQuestion updates question', () => {
    useAppStore.getState().setQuestion('Hello')
    expect(useAppStore.getState().question).toBe('Hello')
  })

  it('setStrategy updates strategy', () => {
    useAppStore.getState().setStrategy('safety_first')
    expect(useAppStore.getState().strategy).toBe('safety_first')
  })

  it('askQuestion sets loading and clears error', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockRecommendResponse()),
    })

    const promise = useAppStore.getState().askQuestion('Where to invest?')
    expect(useAppStore.getState().loading).toBe(true)
    expect(useAppStore.getState().error).toBeNull()
    await promise
  })

  it('askQuestion populates response on success', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve(mockRecommendResponse()),
    })

    await useAppStore.getState().askQuestion('Where to invest?')
    const state = useAppStore.getState()
    expect(state.loading).toBe(false)
    expect(state.response).not.toBeNull()
    expect(state.response!.recommendations).toHaveLength(2)
    expect(state.response!.reasoning_trace).toHaveLength(3)
    expect(state.response!.metadata.total_duration_ms).toBe(100)
  })

  it('askQuestion sets error on failure', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ detail: 'Server error' }),
    })

    await useAppStore.getState().askQuestion('test')
    const state = useAppStore.getState()
    expect(state.loading).toBe(false)
    expect(state.error).toBe('Server error')
    expect(state.response).toBeNull()
  })

  it('askQuestion sets error on network failure', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network down'))

    await useAppStore.getState().askQuestion('test')
    const state = useAppStore.getState()
    expect(state.loading).toBe(false)
    expect(state.error).toBe('Network down')
  })

  it('setActiveStep updates step', () => {
    useAppStore.getState().setActiveStep(2)
    expect(useAppStore.getState().activeStep).toBe(2)
  })
})
