import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Layout from '../components/layout/Layout'

function renderWithRouter(path = '/') {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Layout />
    </MemoryRouter>
  )
}

describe('Layout', () => {
  it('renders CityPulse branding', () => {
    renderWithRouter()
    expect(screen.getByText('CityPulse')).toBeInTheDocument()
  })

  it('renders navigation links', () => {
    renderWithRouter()
    expect(screen.getByText('Ask')).toBeInTheDocument()
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Scenarios')).toBeInTheDocument()
  })

  it('nav links point to correct routes', () => {
    renderWithRouter()
    expect(screen.getByText('Ask').closest('a')).toHaveAttribute('href', '/ask')
    expect(screen.getByText('Dashboard').closest('a')).toHaveAttribute('href', '/dashboard')
    expect(screen.getByText('Scenarios').closest('a')).toHaveAttribute('href', '/scenarios')
  })

  it('brand link goes to landing', () => {
    renderWithRouter()
    const brandLink = screen.getByText('CityPulse').closest('a')
    expect(brandLink).toHaveAttribute('href', '/')
  })

  it('renders footer', () => {
    renderWithRouter()
    expect(screen.getByText(/Built with Google Cloud/)).toBeInTheDocument()
  })

  it('uses dark header on landing page', () => {
    const { container } = renderWithRouter('/')
    const header = container.querySelector('header')
    expect(header?.className).toContain('bg-slate-900')
  })

  it('uses light header on non-landing pages', () => {
    const { container } = renderWithRouter('/ask')
    const header = container.querySelector('header')
    expect(header?.className).toContain('bg-white')
  })

  it('renders an Outlet for child routes', () => {
    const { container } = renderWithRouter()
    expect(container.querySelector('main')).toBeInTheDocument()
  })
})
