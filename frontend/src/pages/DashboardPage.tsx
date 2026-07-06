import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import type { ZoneSummary } from '../types'
import { getZones } from '../services/api'
import { LoadingState, ErrorState } from '../components/common/States'

export default function DashboardPage() {
  const [zones, setZones] = useState<ZoneSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getZones()
      .then(setZones)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingState text="Loading zone data..." />
  if (error) return <ErrorState message={error} onRetry={() => window.location.reload()} />

  const totalComplaints = zones.reduce((s, z) => s + z.complaint_count, 0)
  const avgSeverity = zones.length ? (zones.reduce((s, z) => s + z.avg_severity, 0) / zones.length).toFixed(1) : '0'

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-800 mb-2">Dashboard</h1>
        <p className="text-sm text-slate-500">Overview of all 15 zones and key metrics.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Zones', value: zones.length, color: 'bg-blue-50 border-blue-200' },
          { label: 'Total Complaints', value: totalComplaints, color: 'bg-emerald-50 border-emerald-200' },
          { label: 'Avg Severity', value: avgSeverity, color: 'bg-amber-50 border-amber-200' },
          { label: 'Avg Population', value: Math.round(zones.reduce((s, z) => s + z.population, 0) / zones.length).toLocaleString(), color: 'bg-purple-50 border-purple-200' },
        ].map((kpi, i) => (
          <div key={i} className={`${kpi.color} border rounded-xl p-4`}>
            <div className="text-xs text-slate-500 mb-1">{kpi.label}</div>
            <div className="text-2xl font-bold text-slate-800">{typeof kpi.value === 'number' ? kpi.value.toLocaleString() : kpi.value}</div>
          </div>
        ))}
      </div>

      <div className="grid gap-3">
        <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide mb-2">All Zones</h3>
        {zones.map(zone => (
          <Link key={zone.zone_id} to={`/zones/${zone.zone_id}`}
            className="block p-4 bg-white rounded-xl border border-slate-200 hover:shadow-md hover:border-blue-300 transition-all"
          >
            <div className="flex items-center justify-between">
              <div>
                <span className="font-semibold text-slate-800">{zone.zone_name}</span>
                <span className="text-xs text-slate-400 ml-2">{zone.zone_id}</span>
              </div>
              <div className="flex items-center gap-6 text-sm text-slate-500">
                <span>Pop: {zone.population.toLocaleString()}</span>
                <span>Complaints: {zone.complaint_count}</span>
                <span>Severity: {zone.avg_severity.toFixed(1)}</span>
                <span className="text-slate-400">→</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
