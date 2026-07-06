import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import ScenariosPage from '../pages/ScenariosPage'
import { useAppStore } from '../stores/app'

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

beforeEach(() => {
  mockFetch.mockReset()
  useAppStore.setState({ strategy: 'balanced' })
})

describe('ScenariosPage', () => {
  it('renders page title', () => {
    render(<MemoryRouter><ScenariosPage /></MemoryRouter>)
    expect(screen.getByText('Scenario Simulator')).toBeInTheDocument()
  })

  it('renders empty state initially', () => {
    render(<MemoryRouter><ScenariosPage /></MemoryRouter>)
    expect(screen.getByText(/Adjust the weights on the left/)).toBeInTheDocument()
  })

  it('renders WeightAdjuster component', () => {
    render(<MemoryRouter><ScenariosPage /></MemoryRouter>)
    expect(screen.getByText('Apply & Re-rank')).toBeInTheDocument()
  })
})
