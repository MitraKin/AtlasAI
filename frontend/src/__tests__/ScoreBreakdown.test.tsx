import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import ScoreBreakdownChart from '../components/scoring/ScoreBreakdown'
import type { ScoreBreakdown } from '../types'

const scores: ScoreBreakdown = {
  complaint_volume: 90, severity_index: 85, accident_rate: 80,
  cost_efficiency: 70, population_impact: 60, forecast_trend: 50, equity_factor: 40,
}

describe('ScoreBreakdownChart', () => {
  it('renders zone name in title', () => {
    render(<ScoreBreakdownChart scores={scores} zoneName="Old Town" />)
    expect(screen.getByText('Old Town Score Breakdown')).toBeInTheDocument()
  })

  it('renders a radar chart container', () => {
    const { container } = render(<ScoreBreakdownChart scores={scores} zoneName="Test" />)
    expect(container.querySelector('.recharts-responsive-container')).toBeInTheDocument()
  })

  it('accepts different zone names', () => {
    render(<ScoreBreakdownChart scores={scores} zoneName="Downtown Core" />)
    expect(screen.getByText('Downtown Core Score Breakdown')).toBeInTheDocument()
  })

  it('renders chart content', async () => {
    const { container } = render(<ScoreBreakdownChart scores={scores} zoneName="Test" />)
    await waitFor(() => {
      const svg = container.querySelector('svg')
      expect(svg).toBeTruthy()
    }, { timeout: 5000 })
  })
})
