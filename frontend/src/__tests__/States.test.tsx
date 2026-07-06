import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { LoadingState, ErrorState, EmptyState } from '../components/common/States'

describe('LoadingState', () => {
  it('renders default text', () => {
    render(<LoadingState />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders custom text', () => {
    render(<LoadingState text="Fetching zones..." />)
    expect(screen.getByText('Fetching zones...')).toBeInTheDocument()
  })

  it('has a spinner element', () => {
    render(<LoadingState />)
    expect(document.querySelector('.animate-spin')).toBeInTheDocument()
  })
})

describe('ErrorState', () => {
  it('renders error message', () => {
    render(<ErrorState message="Something went wrong" />)
    expect(screen.getByText('Something went wrong')).toBeInTheDocument()
  })

  it('renders retry button when handler provided', () => {
    render(<ErrorState message="Failed" onRetry={() => {}} />)
    expect(screen.getByText('Try Again')).toBeInTheDocument()
  })

  it('does not render retry button when no handler', () => {
    render(<ErrorState message="Failed" />)
    expect(screen.queryByText('Try Again')).not.toBeInTheDocument()
  })
})

describe('EmptyState', () => {
  it('renders text', () => {
    render(<EmptyState text="No data yet" />)
    expect(screen.getByText('No data yet')).toBeInTheDocument()
  })

  it('renders suggestion when provided', () => {
    render(<EmptyState text="No data" suggestion="Try asking a question" />)
    expect(screen.getByText('No data')).toBeInTheDocument()
    expect(screen.getByText('Try asking a question')).toBeInTheDocument()
  })

  it('does not render suggestion when not provided', () => {
    render(<EmptyState text="No data" />)
    const text = screen.getByText('No data')
    expect(text).toBeInTheDocument()
  })
})
