import '@testing-library/jest-dom/vitest'
import { vi } from 'vitest'

class ResizeObserverMock {
  callback: ResizeObserverCallback
  constructor(callback: ResizeObserverCallback) {
    this.callback = callback
    setTimeout(() => {
      try {
        this.callback([{ contentRect: { width: 500, height: 300 } } as ResizeObserverEntry], this as unknown as ResizeObserver)
      } catch {}
    }, 0)
  }
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverMock as unknown as typeof ResizeObserver

vi.mock('react-leaflet', () => ({
  MapContainer: ({ children }: { children: React.ReactNode }) => children,
  TileLayer: () => null,
  useMap: () => null,
  GeoJSON: () => null,
}))
