import type { ZoneRecommendation } from '../../types'

export default function RecommendationCard({
  rec,
  onClick,
  selected,
}: {
  rec: ZoneRecommendation
  onClick?: () => void
  selected?: boolean
}) {
  const scoreColor = rec.composite_score >= 67 ? 'text-green-600' : rec.composite_score >= 34 ? 'text-amber-600' : 'text-red-600'
  const scoreBg = rec.composite_score >= 67 ? 'bg-green-50 border-green-200' : rec.composite_score >= 34 ? 'bg-amber-50 border-amber-200' : 'bg-red-50 border-red-200'

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-xl border cursor-pointer transition-all hover:shadow-md ${scoreBg} ${selected ? 'ring-2 ring-blue-400 shadow-md' : ''}`}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <span className="text-xs font-bold text-slate-400 mr-2">#{rec.rank}</span>
          <span className="font-semibold text-slate-800">{rec.zone_name}</span>
        </div>
        <span className={`text-lg font-bold ${scoreColor}`}>{rec.composite_score}</span>
      </div>

      <div className="flex items-center gap-3 text-xs text-slate-500 mb-2">
        <span>Confidence: {(rec.confidence * 100).toFixed(0)}%</span>
        <span>Budget: ₹{(rec.suggested_budget_allocation / 100000).toFixed(1)}L</span>
      </div>

      <p className="text-xs text-slate-600 leading-relaxed mb-2">{rec.justification}</p>

      {rec.bias_flags.length > 0 && (
        <div className="mt-2 space-y-1">
          {rec.bias_flags.map((flag, i) => (
            <div key={i} className="text-[11px] text-amber-700 bg-amber-100 rounded px-2 py-1">
              ⚠️ {flag}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
