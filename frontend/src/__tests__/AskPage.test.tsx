import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AskPage from '../pages/AskPage'
import { useAppStore } from '../stores/app'
import type { RecommendResponse } from '../types'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

function mockRecommendResponse(): RecommendResponse {
  return {
    recommendations: [
      {
        rank: 1, zone_id: 'Z13', zone_name: 'University District', composite_score: 73.7, confidence: 1.0,
        suggested_budget_allocation: 750000, justification: 'Strong equity factor and complaint volume',
        scores: { complaint_volume: 90.3, severity_index: 64.5, accident_rate: 69.4, cost_efficiency: 70.4, population_impact: 86.0, forecast_trend: 50.0, equity_factor: 100.0 },
        bias_flags: ['Equity factor is low'], data_citations: ['civic_raw.complaints_311 (zone Z13)'],
      },
      {
        rank: 2, zone_id: 'Z04', zone_name: 'South Market', composite_score: 65.3, confidence: 1.0,
        suggested_budget_allocation: 750000, justification: 'Strong complaint volume and accident rate',
        scores: { complaint_volume: 100.0, severity_index: 0.0, accident_rate: 100.0, cost_efficiency: 53.4, population_impact: 100.0, forecast_trend: 50.0, equity_factor: 100.0 },
        bias_flags: [], data_citations: ['civic_raw.complaints_311 (zone Z04)'],
      },
    ],
    reasoning_trace: [
      { agent: 'data_agent', step: 'Querying infrastructure data', detail: 'Retrieved 15 zones', artifacts: { sql_generated: 'SELECT ...', data_category: 'infrastructure', rows_retrieved: 15 }, duration_ms: 150 },
      { agent: 'reasoning_agent', step: 'Ranking zones', detail: 'Top zone: Z13 with score 73.7', artifacts: { strategy: 'balanced', top_zone_id: 'Z13', top_score: 73.7 }, duration_ms: 0 },
      { agent: 'policy_agent', step: 'Checking equity', detail: 'Equity check passed', artifacts: { equity_flags: [], bias_flags: [] }, duration_ms: 0 },
    ],
    metadata: { total_duration_ms: 151, zones_analyzed: 15, strategy: 'balanced' },
  }
}

beforeEach(() => {
  mockFetch.mockReset()
  useAppStore.setState({
    question: '', strategy: 'balanced', response: null, loading: false, error: null, activeStep: 0,
  })
})

describe('AskPage', () => {
  it('renders page title', () => {
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText('Ask CityPulse')).toBeInTheDocument()
  })

  it('renders text input', () => {
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByPlaceholderText(/We have ₹50L/)).toBeInTheDocument()
  })

  it('renders Ask button', () => {
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText('Ask')).toBeInTheDocument()
  })

  it('renders strategy selector buttons', () => {
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText('balanced')).toBeInTheDocument()
    expect(screen.getByText('safety first')).toBeInTheDocument()
    expect(screen.getByText('cost optimized')).toBeInTheDocument()
  })

  it('renders example question chips', () => {
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText(/₹50L for infrastructure/)).toBeInTheDocument()
    expect(screen.getByText(/safety investment/)).toBeInTheDocument()
  })

  it('renders loading state when loading', () => {
    useAppStore.setState({ loading: true })
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText('Agents are analyzing municipal data...')).toBeInTheDocument()
  })

  it('renders error state with retry', () => {
    useAppStore.setState({ error: 'Something went wrong' })
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    expect(screen.getByText('Try Again')).toBeInTheDocument()
  })

  it('renders recommendations after successful query', () => {
    useAppStore.setState({ response: mockRecommendResponse(), activeStep: 3 })
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText('University District')).toBeInTheDocument()
    expect(screen.getByText('South Market')).toBeInTheDocument()
  })

  it('renders reasoning trail after query', () => {
    useAppStore.setState({ response: mockRecommendResponse(), activeStep: 3 })
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText('data agent')).toBeInTheDocument()
    expect(screen.getByText('reasoning agent')).toBeInTheDocument()
    expect(screen.getByText('policy agent')).toBeInTheDocument()
  })

  it('renders metadata after query', () => {
    useAppStore.setState({ response: mockRecommendResponse(), activeStep: 3 })
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    expect(screen.getByText(/Analyzed 15 zones in 151ms/)).toBeInTheDocument()
    expect(screen.getByText(/Strategy: balanced/)).toBeInTheDocument()
  })

  it('shows view mode toggle buttons after query', () => {
    useAppStore.setState({ response: mockRecommendResponse(), activeStep: 3 })
    render(<MemoryRouter><AskPage /></MemoryRouter>)
    const buttons = screen.getAllByText('Reasoning Trail')
    expect(buttons.length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText('Zone Map')).toBeInTheDocument()
  })
})
