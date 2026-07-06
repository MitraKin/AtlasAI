import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import type { ZoneRecommendation } from '../../types'

function ZoneOverlay({ data, onZoneClick }: {
  data: ZoneRecommendation[]
  onZoneClick: (id: string) => void
  selectedId: string | null
}) {
  const map = useMap()
  const layerRef = useRef<L.GeoJSON | null>(null)

  useEffect(() => {
    fetch('/api/v1/zones')
      .then(r => r.json())
      .then((zones: Array<{ zone_id: string; zone_name: string }>) => {
        if (layerRef.current) {
          map.removeLayer(layerRef.current)
        }

        const scoreMap: Record<string, number> = {}
        data.forEach(d => { scoreMap[d.zone_id] = d.composite_score })

        const features: Array<Record<string, unknown>> = zones.map(z => {
          const idx = parseInt(z.zone_id.slice(1)) - 1
          const row = Math.floor(idx / 5)
          const col = idx % 5
          const lat0 = 17.35 + row * 0.06
          const lon0 = 78.42 + col * 0.04

          return {
            type: 'Feature',
            properties: {
              zone_id: z.zone_id,
              zone_name: z.zone_name,
              score: scoreMap[z.zone_id] || 0,
            },
            geometry: {
              type: 'Polygon',
              coordinates: [[
                [lon0, lat0], [lon0 + 0.036, lat0],
                [lon0 + 0.036, lat0 + 0.054], [lon0, lat0 + 0.054],
                [lon0, lat0],
              ]],
            },
          }
        })

        const layer = L.geoJSON(features as never, {
          style: (f) => {
            const props = f?.properties as Record<string, number> | undefined
            const score = props?.score || 0
            const color = score >= 67 ? '#22c55e' : score >= 34 ? '#f59e0b' : '#ef4444'
            return { fillColor: color, color: '#fff', weight: 1, fillOpacity: 0.6 }
          },
        })

        layer.eachLayer((l) => {
          const featureProps = (l as L.Path & { feature?: { properties?: Record<string, unknown> } }).feature?.properties
          if (featureProps) {
            const zid = featureProps.zone_id as string
            const zname = featureProps.zone_name as string
            const score = featureProps.score as number
            l.bindPopup(`<b>${zname || zid}</b><br/>Score: ${score}`)
            l.on('click', () => onZoneClick(zid))
          }
        })

        layer.addTo(map)
        map.fitBounds(layer.getBounds())
        layerRef.current = layer
      })
  }, [data, map, onZoneClick])

  return null
}

export default function ZoneMap({ recommendations, onZoneClick, selectedId }: {
  recommendations: ZoneRecommendation[]
  onZoneClick: (id: string) => void
  selectedId: string | null
}) {
  return (
    <div className="bg-white rounded-xl border border-slate-200 overflow-hidden h-[500px] relative">
      <MapContainer center={[17.4, 78.48]} zoom={12} className="h-full w-full" zoomControl={false}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <ZoneOverlay data={recommendations} onZoneClick={onZoneClick} selectedId={selectedId} />
      </MapContainer>
      <div className="absolute bottom-3 left-3 bg-white/90 rounded-lg px-3 py-2 text-xs flex gap-3 z-[1000]">
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-green-500" /> High Need</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-amber-500" /> Medium</span>
        <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-500" /> Lower Need</span>
      </div>
    </div>
  )
}
