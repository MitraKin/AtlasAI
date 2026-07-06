import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import Layout from './components/layout/Layout'
import LandingPage from './pages/LandingPage'
import AskPage from './pages/AskPage'
import DashboardPage from './pages/DashboardPage'
import ZoneDetailPage from './pages/ZoneDetailPage'
import ScenariosPage from './pages/ScenariosPage'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<LandingPage />} />
          <Route path="ask" element={<AskPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="zones/:id" element={<ZoneDetailPage />} />
          <Route path="scenarios" element={<ScenariosPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
