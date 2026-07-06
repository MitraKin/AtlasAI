import { useState, useCallback } from 'react'
import { useAppStore } from '../stores/app'
import ReasoningTrail from '../components/reasoning/ReasoningTrail'
import RecommendationCard from '../components/recommendations/RecommendationCard'
import ScoreBreakdownChart from '../components/scoring/ScoreBreakdown'
import ZoneMap from '../components/map/ZoneMap'
import { LoadingState, ErrorState } from '../components/common/States'

const EXAMPLE_QUESTIONS = [
  'We have ₹50L for infrastructure this quarter — where should it go?',
  'Which zones need the most safety investment?',
  'Show me zones with highest sanitation complaints',
  'Where should we allocate budget for road repairs?',
]

export default function AskPage() {
  const { question, response, loading, error, activeStep, strategy, askQuestion, setStrategy } = useAppStore()
  const [input, setInput] = useState(question)
  const [selectedZone, setSelectedZone] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'trail' | 'map'>('trail')

  const handleAsk = useCallback(() => {
    if (input.trim()) askQuestion(input.trim())
  }, [input, askQuestion])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleAsk()
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Ask CityPulse</h1>
        <p className="text-sm text-slate-500">Ask any question about municipal resource allocation and get data-driven, explainable recommendations.</p>
      </div>

      <div className="flex flex-col gap-3 mb-6">
        <div className="flex gap-2">
          <input
            type="text" value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKeyDown}
            placeholder='e.g. "We have ₹50L for infrastructure this quarter — where should it go?"'
            className="flex-1 px-5 py-3 text-sm border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
          />
          <button onClick={handleAsk} disabled={loading || !input.trim()}
            className="px-8 py-3 bg-blue-600 text-white text-sm font-semibold rounded-xl hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Analyzing...' : 'Ask'}
          </button>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400">Strategy:</span>
          {(['balanced', 'safety_first', 'cost_optimized'] as const).map(s => (
            <button key={s}
              className={`text-xs px-3 py-1 rounded-full border transition-colors ${strategy === s ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-500 border-slate-300 hover:border-blue-400'}`}
              onClick={() => setStrategy(s)}
            >
              {s.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-8">
        {EXAMPLE_QUESTIONS.map((q, i) => (
          <button key={i}
            onClick={() => { setInput(q); askQuestion(q) }}
            className="text-xs px-3 py-1.5 bg-slate-100 text-slate-600 rounded-full hover:bg-slate-200 transition-colors"
          >
            {q.length > 55 ? q.slice(0, 55) + '...' : q}
          </button>
        ))}
      </div>

      {loading && <LoadingState text="Agents are analyzing municipal data..." />}
      {error && <ErrorState message={error} onRetry={handleAsk} />}

      {response && !loading && (
        <div className="space-y-6">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Analyzed {response.metadata.zones_analyzed} zones in {response.metadata.total_duration_ms}ms</span>
            <span>·</span>
            <span>Strategy: {response.metadata.strategy.replace('_', ' ')}</span>
          </div>

          <div className="flex gap-4 mb-4">
            <button onClick={() => setViewMode('trail')}
              className={`text-xs px-4 py-1.5 rounded-lg border transition-colors ${viewMode === 'trail' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-600 border-slate-300'}`}
            >
              Reasoning Trail
            </button>
            <button onClick={() => setViewMode('map')}
              className={`text-xs px-4 py-1.5 rounded-lg border transition-colors ${viewMode === 'map' ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-600 border-slate-300'}`}
            >
              Zone Map
            </button>
          </div>

          <div className="grid lg:grid-cols-5 gap-6">
            <div className="lg:col-span-2 space-y-4">
              {viewMode === 'trail' ? (
                <ReasoningTrail steps={response.reasoning_trace} activeStep={activeStep || 3} />
              ) : (
                <ZoneMap
                  recommendations={response.recommendations}
                  onZoneClick={setSelectedZone}
                  selectedId={selectedZone}
                />
              )}
            </div>

            <div className="lg:col-span-2 space-y-3">
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Recommendations</h3>
              {response.recommendations.map(rec => (
                <RecommendationCard
                  key={rec.rank}
                  rec={rec}
                  selected={selectedZone === rec.zone_id}
                  onClick={() => setSelectedZone(selectedZone === rec.zone_id ? null : rec.zone_id)}
                />
              ))}
            </div>

            <div className="lg:col-span-1">
              {selectedZone && (() => {
                const zone = response.recommendations.find(r => r.zone_id === selectedZone)
                return zone ? <ScoreBreakdownChart scores={zone.scores} zoneName={zone.zone_name} /> : null
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
