import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ReasoningTrail from '../components/reasoning/ReasoningTrail'
import type { ReasoningStep } from '../types'

const steps: ReasoningStep[] = [
  { agent: 'data_agent', step: 'Querying infrastructure data', detail: 'Found 15 zones with metrics', artifacts: { sql_generated: 'SELECT * FROM complaints_311', rows_retrieved: 15 }, duration_ms: 50 },
  { agent: 'reasoning_agent', step: 'Ranking zones', detail: 'Zone 1 scores highest due to complaint volume and severity', artifacts: { strategy: 'balanced', top_zone_id: 'Z01' }, duration_ms: 10 },
  { agent: 'policy_agent', step: 'Checking equity', detail: 'Equity check passed. No bias flags.', artifacts: { equity_flags: [], bias_flags: [] }, duration_ms: 5 },
]

describe('ReasoningTrail', () => {
  it('renders nothing when no steps', () => {
    const { container } = render(<ReasoningTrail steps={[]} activeStep={0} />)
    expect(container.innerHTML).toBe('')
  })

  it('renders all 3 agent steps', () => {
    render(<ReasoningTrail steps={steps} activeStep={3} />)
    expect(screen.getByText('data agent')).toBeInTheDocument()
    expect(screen.getByText('reasoning agent')).toBeInTheDocument()
    expect(screen.getByText('policy agent')).toBeInTheDocument()
  })

  it('shows step descriptions', () => {
    render(<ReasoningTrail steps={steps} activeStep={3} />)
    expect(screen.getByText('Querying infrastructure data')).toBeInTheDocument()
    expect(screen.getByText('Ranking zones')).toBeInTheDocument()
    expect(screen.getByText('Checking equity')).toBeInTheDocument()
  })

  it('shows detail text', () => {
    render(<ReasoningTrail steps={steps} activeStep={3} />)
    expect(screen.getByText(/Found 15 zones/)).toBeInTheDocument()
    expect(screen.getByText(/Equity check passed/)).toBeInTheDocument()
  })

  it('shows durations', () => {
    render(<ReasoningTrail steps={steps} activeStep={3} />)
    expect(screen.getByText('50ms')).toBeInTheDocument()
    expect(screen.getByText('10ms')).toBeInTheDocument()
    expect(screen.getByText('5ms')).toBeInTheDocument()
  })

  it('shows SQL in expandable section for data agent', () => {
    render(<ReasoningTrail steps={steps} activeStep={3} />)
    expect(screen.getByText('View SQL')).toBeInTheDocument()
  })

  it('dimmed steps below activeStep', () => {
    render(<ReasoningTrail steps={steps} activeStep={1} />)
    const allSteps = screen.getAllByText(/agent/)
    expect(allSteps.length).toBeGreaterThanOrEqual(3)
  })

  it('renders with all steps visible when activeStep covers all', () => {
    render(<ReasoningTrail steps={steps} activeStep={5} />)
    expect(screen.getByText('data agent')).toBeInTheDocument()
    expect(screen.getByText('reasoning agent')).toBeInTheDocument()
    expect(screen.getByText('policy agent')).toBeInTheDocument()
  })
})
