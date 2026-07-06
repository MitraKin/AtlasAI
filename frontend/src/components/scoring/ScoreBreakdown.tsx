import type { ScoreBreakdown } from '../../types'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts'

export default function ScoreBreakdownChart({ scores, zoneName }: { scores: ScoreBreakdown; zoneName: string }) {
  const data = [
    { factor: 'Complaints', value: scores.complaint_volume, fullMark: 100 },
    { factor: 'Severity', value: scores.severity_index, fullMark: 100 },
    { factor: 'Accidents', value: scores.accident_rate, fullMark: 100 },
    { factor: 'Cost Eff.', value: scores.cost_efficiency, fullMark: 100 },
    { factor: 'Pop. Impact', value: scores.population_impact, fullMark: 100 },
    { factor: 'Forecast', value: scores.forecast_trend, fullMark: 100 },
    { factor: 'Equity', value: scores.equity_factor, fullMark: 100 },
  ]

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <h4 className="text-sm font-semibold text-slate-700 mb-2">{zoneName} Score Breakdown</h4>
      <ResponsiveContainer width="100%" height={250}>
        <RadarChart data={data}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="factor" tick={{ fontSize: 10, fill: '#64748b' }} />
          <PolarRadiusAxis angle={90} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar name="Score" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
