import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import LandingPage from '../pages/LandingPage'

describe('LandingPage', () => {
  it('renders hero heading', () => {
    render(<MemoryRouter><LandingPage /></MemoryRouter>)
    expect(screen.getByText(/AI Copilot for/)).toBeInTheDocument()
    expect(screen.getByText(/Municipal Decisions/)).toBeInTheDocument()
  })

  it('renders CTA button linking to ask page', () => {
    render(<MemoryRouter><LandingPage /></MemoryRouter>)
    const cta = screen.getByText('Try CityPulse Now →')
    expect(cta.closest('a')).toHaveAttribute('href', '/ask')
  })

  it('renders 3 feature cards', () => {
    render(<MemoryRouter><LandingPage /></MemoryRouter>)
    expect(screen.getByText('Visible Reasoning')).toBeInTheDocument()
    expect(screen.getByText('Bias Detection')).toBeInTheDocument()
    expect(screen.getByText('What-If Scenarios')).toBeInTheDocument()
  })

  it('renders 3-agent explanation section', () => {
    render(<MemoryRouter><LandingPage /></MemoryRouter>)
    expect(screen.getByText('Data Agent')).toBeInTheDocument()
    expect(screen.getByText('Reasoning Agent')).toBeInTheDocument()
    expect(screen.getByText('Policy Agent')).toBeInTheDocument()
  })

  it('renders Google Cloud tech badges', () => {
    render(<MemoryRouter><LandingPage /></MemoryRouter>)
    expect(screen.getByText('BigQuery')).toBeInTheDocument()
    expect(screen.getByText('Gemini')).toBeInTheDocument()
    expect(screen.getByText('ADK')).toBeInTheDocument()
    expect(screen.getByText('Cloud Run')).toBeInTheDocument()
    expect(screen.getByText('Looker')).toBeInTheDocument()
    expect(screen.getByText('Vertex AI')).toBeInTheDocument()
  })
})
