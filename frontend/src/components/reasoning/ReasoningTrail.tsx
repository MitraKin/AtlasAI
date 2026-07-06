import type { ReasoningStep } from '../../types'

const AGENT_CONFIG: Record<string, { icon: string; color: string; bg: string; border: string }> = {
  data_agent: { icon: '📊', color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-200' },
  reasoning_agent: { icon: '🧠', color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-200' },
  policy_agent: { icon: '⚖️', color: 'text-rose-700', bg: 'bg-rose-50', border: 'border-rose-200' },
}

export default function ReasoningTrail({ steps, activeStep }: { steps: ReasoningStep[]; activeStep: number }) {
  if (!steps.length) return null

  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wide">Reasoning Trail</h3>
      <div className="relative pl-6 border-l-2 border-slate-200 space-y-4">
        {steps.map((step, i) => {
          const cfg = AGENT_CONFIG[step.agent] || AGENT_CONFIG.data_agent
          const visible = i < activeStep
          const animating = i === activeStep - 1

          return (
            <div key={i} className={`relative ${visible ? 'opacity-100' : 'opacity-30'} transition-opacity duration-500`}>
              <div className={`absolute -left-[26px] top-1 w-4 h-4 rounded-full ${cfg.bg} border-2 ${cfg.border} ${animating ? 'animate-pulse' : ''}`}>
                <span className="block text-[10px] leading-none text-center">{step.agent === 'data_agent' ? 'D' : step.agent === 'reasoning_agent' ? 'R' : 'P'}</span>
              </div>
              <div className={`${cfg.bg} ${cfg.border} border rounded-lg p-3`}>
                <div className="flex items-center gap-2 mb-1">
                  <span>{cfg.icon}</span>
                  <span className={`text-xs font-semibold ${cfg.color} uppercase`}>{step.agent.replace('_', ' ')}</span>
                  <span className="text-xs text-slate-400 ml-auto">{step.duration_ms}ms</span>
                </div>
                <p className="text-xs text-slate-500 mb-1">{step.step}</p>
                <p className="text-xs text-slate-600 leading-relaxed">{step.detail}</p>
                {(step.artifacts && typeof step.artifacts === 'object' && 'sql_generated' in step.artifacts) && (
                  <details className="mt-2">
                    <summary className="text-xs text-blue-600 cursor-pointer hover:underline">View SQL</summary>
                    <pre className="mt-1 p-2 bg-slate-900 text-green-400 text-[11px] rounded overflow-x-auto max-h-32">
                      {String(step.artifacts.sql_generated)}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
