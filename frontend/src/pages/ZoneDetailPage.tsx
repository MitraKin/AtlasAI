import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { LoadingState, ErrorState } from '../components/common/States'

interface ZoneDetail {
  zone_id: string; zone_name: string; population: number; area_sqkm: number
  median_income: number; population_density: number; poverty_rate: number
  complaint_stats: Record<string, number>
  budget_history: Array<Record<string, number>>
  infrastructure: Array<Record<string, number>>
}

export default function ZoneDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [zone, setZone] = useState<ZoneDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`/api/v1/zones/${id}`)
      .then(r => { if (!r.ok) throw new Error('Zone not found'); return r.json() })
      .then(setZone)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingState text="Loading zone details..." />
  if (error) return <ErrorState message={error} />
  if (!zone) return null

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <Link to="/dashboard" className="text-xs text-blue-600 hover:underline mb-4 inline-block">← Back to Dashboard</Link>
      <div className="flex items-center gap-3 mb-6">
        <h1 className="text-2xl font-bold text-slate-800">{zone.zone_name}</h1>
        <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">{zone.zone_id}</span>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Population', value: zone.population.toLocaleString() },
          { label: 'Median Income', value: `₹${(zone.median_income / 1000).toFixed(0)}K` },
          { label: 'Poverty Rate', value: `${(zone.poverty_rate * 100).toFixed(0)}%` },
          { label: 'Area', value: `${zone.area_sqkm} km²` },
          { label: 'Density', value: `${zone.population_density}/km²` },
          { label: 'Total Complaints', value: zone.complaint_stats.total_complaints || 0 },
        ].map((s, i) => (
          <div key={i} className="bg-white border border-slate-200 rounded-xl p-4">
            <div className="text-xs text-slate-400 mb-1">{s.label}</div>
            <div className="text-lg font-semibold text-slate-800">{s.value}</div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Complaint Stats</h3>
          <dl className="space-y-2 text-sm">
            {Object.entries(zone.complaint_stats).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <dt className="text-slate-500 capitalize">{k.replace(/_/g, ' ')}</dt>
                <dd className="font-medium text-slate-800">{typeof v === 'number' ? v.toFixed(1) : v}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Infrastructure</h3>
          <div className="space-y-2">
            {zone.infrastructure.map((asset, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="text-slate-600 capitalize">{asset.asset_type?.toString().replace(/_/g, ' ')}</span>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-400">{asset.avg_age_years?.toString()}yr avg</span>
                  <div className="w-20 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${Number(asset.condition_score) >= 7 ? 'bg-green-500' : Number(asset.condition_score) >= 4 ? 'bg-amber-500' : 'bg-red-500'}`}
                      style={{ width: `${(Number(asset.condition_score) || 0) * 10}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium">{asset.condition_score}/10</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
