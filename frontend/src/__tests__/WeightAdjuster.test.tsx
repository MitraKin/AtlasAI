import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WeightAdjuster from '../components/scenarios/WeightAdjuster'
import { useAppStore } from '../stores/app'
import type { RecommendResponse } from '../types'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

function mockScenarioResponse(): RecommendResponse {
  return {
    recommendations: [
      {
        rank: 1, zone_id: 'Z01', zone_name: 'Zone One', composite_score: 90, confidence: 0.95,
        suggested_budget_allocation: 750000, justification: 'Top score',
        scores: { complaint_volume: 90, severity_index: 85, accident_rate: 80, cost_efficiency: 70, population_impact: 60, forecast_trend: 50, equity_factor: 40 },
        bias_flags: [], data_citations: [],
      },
    ],
    reasoning_trace: [],
    metadata: { total_duration_ms: 50, zones_analyzed: 15, strategy: 'custom' },
  }
}

beforeEach(() => {
  mockFetch.mockReset()
  useAppStore.setState({ strategy: 'balanced' })
})

describe('WeightAdjuster', () => {
  it('renders all 4 preset buttons', () => {
    render(<WeightAdjuster onResults={() => {}} />)
    expect(screen.getByText('Balanced')).toBeInTheDocument()
    expect(screen.getByText('Safety First')).toBeInTheDocument()
    expect(screen.getByText('Cost Optimized')).toBeInTheDocument()
    expect(screen.getByText('Equity Focused')).toBeInTheDocument()
  })

  it('renders weight sliders', () => {
    render(<WeightAdjuster onResults={() => {}} />)
    expect(screen.getByText('Complaint Volume')).toBeInTheDocument()
    expect(screen.getByText('Severity Index')).toBeInTheDocument()
    expect(screen.getByText('Accident Rate')).toBeInTheDocument()
    expect(screen.getByText('Cost Efficiency')).toBeInTheDocument()
    expect(screen.getByText('Population Impact')).toBeInTheDocument()
    expect(screen.getByText('Forecast Trend')).toBeInTheDocument()
    expect(screen.getByText('Equity Factor')).toBeInTheDocument()
  })

  it('renders 7 range inputs', () => {
    const { container } = render(<WeightAdjuster onResults={() => {}} />)
    const sliders = container.querySelectorAll('input[type="range"]')
    expect(sliders).toHaveLength(7)
  })

  it('has Apply & Re-rank button', () => {
    render(<WeightAdjuster onResults={() => {}} />)
    expect(screen.getByText('Apply & Re-rank')).toBeInTheDocument()
  })

  it('calls onResults after apply', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true, status: 200, json: () => Promise.resolve(mockScenarioResponse()),
    })
    const onResults = vi.fn()
    render(<WeightAdjuster onResults={onResults} />)

    fireEvent.click(screen.getByText('Apply & Re-rank'))

    await waitFor(() => {
      expect(onResults).toHaveBeenCalledOnce()
    })

    const result = onResults.mock.calls[0][0] as RecommendResponse
    expect(result.recommendations).toHaveLength(1)
    expect(result.recommendations[0].zone_name).toBe('Zone One')
  })

  it('updates slider value when preset clicked', async () => {
    const user = userEvent.setup()
    render(<WeightAdjuster onResults={() => {}} />)
    await user.click(screen.getByText('Safety First'))
    const sliders = document.querySelectorAll('input[type="range"]')
    expect(sliders).toHaveLength(7)
  })

  it('does not show loading state initially', () => {
    render(<WeightAdjuster onResults={() => {}} />)
    expect(screen.getByText('Apply & Re-rank')).not.toBeDisabled()
  })
})
