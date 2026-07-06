import { useState } from 'react'
import { useAppStore } from '../../stores/app'
import { postScenario } from '../../services/api'
import type { RecommendResponse } from '../../types'

const DEFAULT_WEIGHTS = {
  complaint_volume: 0.20, severity_index: 0.25, accident_rate: 0.20,
  cost_efficiency: 0.10, population_impact: 0.10, forecast_trend: 0.10, equity_factor: 0.05,
}

const LABELS: Record<string, string> = {
  complaint_volume: 'Complaint Volume', severity_index: 'Severity Index',
  accident_rate: 'Accident Rate', cost_efficiency: 'Cost Efficiency',
  population_impact: 'Population Impact', forecast_trend: 'Forecast Trend',
  equity_factor: 'Equity Factor',
}

export default function WeightAdjuster({ onResults }: { onResults: (r: RecommendResponse) => void }) {
  const strategy = useAppStore(s => s.strategy)
  const setStrategy = useAppStore(s => s.setStrategy)
  const [weights, setWeights] = useState<Record<string, number>>({ ...DEFAULT_WEIGHTS })
  const [loading, setLoading] = useState(false)

  const presets: { label: string; value: string; w: Record<string, number> }[] = [
    { label: 'Balanced', value: 'balanced', w: { complaint_volume: 0.20, severity_index: 0.25, accident_rate: 0.20, cost_efficiency: 0.10, population_impact: 0.10, forecast_trend: 0.10, equity_factor: 0.05 } },
    { label: 'Safety First', value: 'safety_first', w: { complaint_volume: 0.10, severity_index: 0.30, accident_rate: 0.30, cost_efficiency: 0.05, population_impact: 0.10, forecast_trend: 0.10, equity_factor: 0.05 } },
    { label: 'Cost Optimized', value: 'cost_optimized', w: { complaint_volume: 0.15, severity_index: 0.15, accident_rate: 0.15, cost_efficiency: 0.30, population_impact: 0.10, forecast_trend: 0.10, equity_factor: 0.05 } },
    { label: 'Equity Focused', value: 'equity_focused', w: { complaint_volume: 0.15, severity_index: 0.20, accident_rate: 0.15, cost_efficiency: 0.10, population_impact: 0.15, forecast_trend: 0.10, equity_factor: 0.15 } },
  ]

  const applyPreset = (p: typeof presets[0]) => {
    setWeights({ ...p.w })
    setStrategy(p.value as typeof strategy)
  }

  const handleSlider = (key: string, value: number) => {
    const updated = { ...weights, [key]: value / 100 }
    setWeights(updated)
  }

  const run = async () => {
    setLoading(true)
    try {
      const result = await postScenario('re-rank', weights)
      onResults(result)
    } catch { /* ignore */ }
    setLoading(false)
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <h4 className="text-sm font-semibold text-slate-700 mb-3">Adjust Strategy Weights</h4>
      <div className="flex flex-wrap gap-2 mb-4">
        {presets.map(p => (
          <button key={p.value} onClick={() => applyPreset(p)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${strategy === p.value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-600 border-slate-300 hover:border-blue-400'}`}
          >
            {p.label}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        {Object.entries(weights).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-xs text-slate-500 mb-1">
              <span>{LABELS[key] || key}</span>
              <span className="font-mono">{val.toFixed(2)}</span>
            </div>
            <input type="range" min={0} max={100} value={Math.round(val * 100)}
              onChange={e => handleSlider(key, parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
          </div>
        ))}
      </div>
      <button onClick={run} disabled={loading}
        className="mt-4 w-full py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
      >
        {loading ? 'Re-ranking...' : 'Apply & Re-rank'}
      </button>
    </div>
  )
}
