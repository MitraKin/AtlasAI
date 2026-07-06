import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import RecommendationCard from '../components/recommendations/RecommendationCard'
import type { ZoneRecommendation } from '../types'

const rec: ZoneRecommendation = {
  rank: 1, zone_id: 'Z07', zone_name: 'Old Town', composite_score: 87,
  confidence: 0.92, suggested_budget_allocation: 1800000,
  justification: 'Highest complaint density and aging infrastructure',
  scores: { complaint_volume: 90, severity_index: 85, accident_rate: 80, cost_efficiency: 70, population_impact: 60, forecast_trend: 50, equity_factor: 40 },
  bias_flags: ['Safety weighted 2x over convenience'],
  data_citations: ['civic_raw.complaints_311'],
}

const lowScoreRec: ZoneRecommendation = {
  rank: 10, zone_id: 'Z14', zone_name: 'Hilltop', composite_score: 25,
  confidence: 0.75, suggested_budget_allocation: 500000,
  justification: 'Lower complaint volume but some infrastructure needs',
  scores: { complaint_volume: 30, severity_index: 25, accident_rate: 20, cost_efficiency: 10, population_impact: 15, forecast_trend: 50, equity_factor: 40 },
  bias_flags: [],
  data_citations: [],
}

describe('RecommendationCard', () => {
  it('renders zone name and rank', () => {
    render(<RecommendationCard rec={rec} />)
    expect(screen.getByText('Old Town')).toBeInTheDocument()
    expect(screen.getByText('#1')).toBeInTheDocument()
  })

  it('renders composite score', () => {
    render(<RecommendationCard rec={rec} />)
    expect(screen.getByText('87')).toBeInTheDocument()
  })

  it('renders confidence percentage', () => {
    render(<RecommendationCard rec={rec} />)
    expect(screen.getByText('Confidence: 92%')).toBeInTheDocument()
  })

  it('renders budget allocation in lakhs', () => {
    render(<RecommendationCard rec={rec} />)
    expect(screen.getByText('Budget: ₹18.0L')).toBeInTheDocument()
  })

  it('renders justification', () => {
    render(<RecommendationCard rec={rec} />)
    expect(screen.getByText('Highest complaint density and aging infrastructure')).toBeInTheDocument()
  })

  it('renders bias flags', () => {
    render(<RecommendationCard rec={rec} />)
    expect(screen.getByText(/Safety weighted/)).toBeInTheDocument()
  })

  it('no bias flags when empty', () => {
    render(<RecommendationCard rec={lowScoreRec} />)
    const flags = screen.queryByText(/⚠️/)
    expect(flags).not.toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<RecommendationCard rec={rec} onClick={handleClick} />)
    fireEvent.click(screen.getByText('Old Town'))
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('applies selected styling when selected', () => {
    const { container } = render(<RecommendationCard rec={rec} selected />)
    const card = container.firstElementChild
    expect(card?.className).toContain('ring-2')
    expect(card?.className).toContain('ring-blue-400')
  })

  it('uses green styling for high scores', () => {
    render(<RecommendationCard rec={rec} />)
    const score = screen.getByText('87')
    expect(score.className).toContain('text-green-600')
  })

  it('uses red styling for low scores', () => {
    render(<RecommendationCard rec={lowScoreRec} />)
    const score = screen.getByText('25')
    expect(score.className).toContain('text-red-600')
  })
})
