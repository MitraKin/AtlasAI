import { Link } from 'react-router-dom'

export default function LandingPage() {
  return (
    <div>
      <section className="bg-slate-900 text-white py-24">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 leading-tight">
            AI Copilot for <span className="text-blue-400">Municipal Decisions</span>
          </h1>
          <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
            Ask natural language questions about resource allocation and get ranked,
            explainable recommendations backed by data — with full transparency on how the AI thinks.
          </p>
          <Link to="/ask" className="inline-block px-8 py-3 bg-blue-600 text-white text-lg font-semibold rounded-xl hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/30">
            Try CityPulse Now →
          </Link>
        </div>
      </section>

      <section className="py-20 max-w-6xl mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-8">
          {[
            { icon: '🔍', title: 'Visible Reasoning', desc: 'Every recommendation shows its reasoning trail — which data was queried, how scores were calculated, and what biases were checked.' },
            { icon: '⚖️', title: 'Bias Detection', desc: 'The Policy Agent automatically flags if budget allocation skews toward privileged zones or if certain factors are weighted unfairly.' },
            { icon: '🎯', title: 'What-If Scenarios', desc: 'Adjust weights for safety, cost, equity, or create custom strategies. See rankings change in real-time as priorities shift.' },
          ].map((f, i) => (
            <div key={i} className="p-6 rounded-xl border border-slate-200 hover:shadow-lg transition-shadow">
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="py-16 bg-slate-50">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold mb-4">Three Agents, One Decision</h2>
          <div className="grid md:grid-cols-3 gap-6 mt-8">
            {[
              { agent: 'Data Agent', bg: 'bg-emerald-100', text: 'text-emerald-800', desc: 'Finds facts — queries civic data, generates SQL, retrieves structured results' },
              { agent: 'Reasoning Agent', bg: 'bg-amber-100', text: 'text-amber-800', desc: 'Weighs tradeoffs — applies multi-criteria scoring across 7 factors' },
              { agent: 'Policy Agent', bg: 'bg-rose-100', text: 'text-rose-800', desc: 'Checks fairness — flags bias, cites sources, generates explanations' },
            ].map((a, i) => (
              <div key={i} className={`${a.bg} rounded-xl p-5`}>
                <div className={`text-xs font-bold uppercase mb-2 ${a.text}`}>{a.agent}</div>
                <p className="text-sm text-slate-600">{a.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 text-center">
        <p className="text-sm text-slate-400 mb-4">Built with Google Cloud</p>
        <div className="flex justify-center gap-4 text-xs text-slate-500">
          <span className="px-3 py-1 bg-slate-100 rounded-full">BigQuery</span>
          <span className="px-3 py-1 bg-slate-100 rounded-full">Gemini</span>
          <span className="px-3 py-1 bg-slate-100 rounded-full">ADK</span>
          <span className="px-3 py-1 bg-slate-100 rounded-full">Cloud Run</span>
          <span className="px-3 py-1 bg-slate-100 rounded-full">Looker</span>
          <span className="px-3 py-1 bg-slate-100 rounded-full">Vertex AI</span>
        </div>
      </section>
    </div>
  )
}
