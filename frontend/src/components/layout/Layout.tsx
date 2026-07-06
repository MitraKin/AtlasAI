import { Outlet, Link, useLocation } from 'react-router-dom'

export default function Layout() {
  const location = useLocation()
  const isLanding = location.pathname === '/'

  return (
    <div className="min-h-screen flex flex-col">
      <header className={`${isLanding ? 'bg-slate-900 text-white' : 'bg-white border-b border-slate-200'} sticky top-0 z-50`}>
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-bold text-lg">
            <span className="text-xl">🏙️</span>
            <span>CityPulse</span>
          </Link>
          <nav className="flex items-center gap-6 text-sm font-medium">
            <Link to="/ask" className={`hover:text-blue-600 transition-colors ${location.pathname === '/ask' ? 'text-blue-600' : ''}`}>
              Ask
            </Link>
            <Link to="/dashboard" className={`hover:text-blue-600 transition-colors ${location.pathname === '/dashboard' ? 'text-blue-600' : ''}`}>
              Dashboard
            </Link>
            <Link to="/scenarios" className={`hover:text-blue-600 transition-colors ${location.pathname === '/scenarios' ? 'text-blue-600' : ''}`}>
              Scenarios
            </Link>
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="bg-slate-900 text-slate-400 text-xs py-6 text-center">
        CityPulse — AI Civic Decision Copilot · Built with Google Cloud
      </footer>
    </div>
  )
}
