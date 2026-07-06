import { create } from 'zustand'
import type { RecommendResponse, ReasoningStep, Strategy } from '../types'
import { postRecommendation } from '../services/api'

interface AppState {
  question: string
  strategy: Strategy
  response: RecommendResponse | null
  loading: boolean
  error: string | null
  activeStep: number

  setQuestion: (q: string) => void
  setStrategy: (s: Strategy) => void
  askQuestion: (q: string) => Promise<void>
  setActiveStep: (step: number) => void
}

export const useAppStore = create<AppState>((set) => ({
  question: '',
  strategy: 'balanced' as Strategy,
  response: null,
  loading: false,
  error: null,
  activeStep: 0,

  setQuestion: (q) => set({ question: q }),
  setStrategy: (s) => set({ strategy: s }),

  askQuestion: async (q: string) => {
    set({ loading: true, error: null, response: null, question: q, activeStep: 0 })
    try {
      const response = await postRecommendation(q, useAppStore.getState().strategy)
      set({ response, loading: false })

      response.reasoning_trace.forEach((_, i) => {
        setTimeout(() => set({ activeStep: i + 1 }), (i + 1) * 600)
      })
    } catch (e) {
      set({ error: e instanceof Error ? e.message : 'Something went wrong', loading: false })
    }
  },

  setActiveStep: (step) => set({ activeStep: step }),
}))
