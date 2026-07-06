import { useState } from 'react'
import WeightAdjuster from '../components/scenarios/WeightAdjuster'
import RecommendationCard from '../components/recommendations/RecommendationCard'
import type { RecommendResponse } from '../types'
import { EmptyState } from '../components/common/States'

export default function ScenariosPage() {
  const [results, setResults] = useState<RecommendResponse | null>(null)
  const [selectedZone, setSelectedZone] = useState<string | null>(null)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Scenario Simulator</h1>
        <p className="text-sm text-slate-500">Adjust scoring weights and see how rankings shift in real-time.</p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <WeightAdjuster onResults={setResults} />
        </div>

        <div className="lg:col-span-2">
          {results ? (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">
                Re-ranked Zones ({results.recommendations.length})
              </h3>
              {results.recommendations.map(rec => (
                <RecommendationCard
                  key={rec.rank}
                  rec={rec}
                  selected={selectedZone === rec.zone_id}
                  onClick={() => setSelectedZone(selectedZone === rec.zone_id ? null : rec.zone_id)}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              text="Adjust the weights on the left and click 'Apply & Re-rank' to see how priorities change."
              suggestion="Try switching between Balanced, Safety First, and Equity Focused presets."
            />
          )}
        </div>
      </div>
    </div>
  )
}
