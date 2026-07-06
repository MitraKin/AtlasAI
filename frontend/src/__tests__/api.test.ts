import { describe, it, expect, vi, beforeEach } from 'vitest'
import { postRecommendation, postChat, postScenario, getZones } from '../services/api'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

function mockResponse(data: unknown, status = 200) {
  return { ok: status >= 200 && status < 300, status, json: () => Promise.resolve(data) }
}

beforeEach(() => {
  mockFetch.mockReset()
})

describe('postRecommendation', () => {
  it('calls the correct endpoint with payload', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({
      recommendations: [], reasoning_trace: [], metadata: { total_duration_ms: 100, zones_analyzed: 15, strategy: 'balanced' }
    }))

    const result = await postRecommendation('Where should ₹50L go?', 'balanced')
    expect(mockFetch).toHaveBeenCalledWith('/api/v1/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'Where should ₹50L go?', strategy: 'balanced', max_results: 10 }),
    })
    expect(result.recommendations).toEqual([])
    expect(result.metadata.strategy).toBe('balanced')
  })

  it('throws on non-ok response', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ detail: 'Server error' }, 500))
    await expect(postRecommendation('test', 'balanced')).rejects.toThrow('Server error')
  })

  it('throws on network failure', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'))
    await expect(postRecommendation('test', 'balanced')).rejects.toThrow('Network error')
  })
})

describe('postChat', () => {
  it('calls chat endpoint', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({ answer: 'Hello', citations: [] }))
    const result = await postChat('Why?')
    expect(mockFetch).toHaveBeenCalledWith('/api/v1/chat', expect.objectContaining({
      body: JSON.stringify({ question: 'Why?', context: undefined }),
    }))
    expect(result.answer).toBe('Hello')
  })
})

describe('postScenario', () => {
  it('calls scenario endpoint with weights', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse({
      recommendations: [], reasoning_trace: [], metadata: { total_duration_ms: 50, zones_analyzed: 10, strategy: 'custom' }
    }))
    const weights = { complaint_volume: 0.3, severity_index: 0.7 }
    await postScenario('re-rank', weights)
    expect(mockFetch).toHaveBeenCalledWith('/api/v1/scenarios', expect.objectContaining({
      body: JSON.stringify({ question: 're-rank', weights }),
    }))
  })
})

describe('getZones', () => {
  it('calls zones list endpoint', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse([
      { zone_id: 'Z01', zone_name: 'Downtown', population: 50000, area_sqkm: 10, median_income: 60000, complaint_count: 100, avg_severity: 3.2, composite_score: null }
    ]))
    const zones = await getZones()
    expect(mockFetch).toHaveBeenCalledWith('/api/v1/zones')
    expect(zones).toHaveLength(1)
    expect(zones[0].zone_name).toBe('Downtown')
  })

  it('throws on failure', async () => {
    mockFetch.mockResolvedValueOnce(mockResponse(null, 500))
    await expect(getZones()).rejects.toThrow('Request failed')
  })
})
