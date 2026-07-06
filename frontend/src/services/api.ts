import type { RecommendResponse, ZoneSummary, ChatMessage, Strategy } from '../types'

const API = '/api/v1'

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`)
  if (!res.ok) throw new Error('Request failed')
  return res.json()
}

export function postRecommendation(question: string, strategy: Strategy): Promise<RecommendResponse> {
  return post<RecommendResponse>('/recommend', { question, strategy, max_results: 10 })
}

export function postChat(question: string, context?: Record<string, unknown>): Promise<ChatMessage> {
  return post<ChatMessage>('/chat', { question, context })
}

export function postScenario(question: string, weights: Record<string, number>): Promise<RecommendResponse> {
  return post<RecommendResponse>('/scenarios', { question, weights })
}

export function getZones(): Promise<ZoneSummary[]> {
  return get<ZoneSummary[]>('/zones')
}
