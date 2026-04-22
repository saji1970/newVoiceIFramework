import { useEffect, useState } from 'react'
import { api } from '../api/client'

interface Provider {
  name: string
  available: boolean
  models: string[]
}

export default function ProvidersPage() {
  const [providers, setProviders] = useState<Provider[]>([])
  const [health, setHealth] = useState<{ status: string; uptime_seconds: number; version: string } | null>(null)

  useEffect(() => {
    api.getProviders().then((res) => setProviders(res.providers)).catch(() => {})
    api.getHealth().then(setHealth).catch(() => {})
  }, [])

  return (
    <div className="p-6">
      {/* Server Status */}
      {health && (
        <div className="bg-white border rounded-xl p-4 mb-6">
          <h3 className="font-semibold text-gray-900 mb-2">Server Status</h3>
          <div className="flex gap-6 text-sm">
            <div>
              <span className="text-gray-500">Status: </span>
              <span className="text-green-600 font-medium">{health.status}</span>
            </div>
            <div>
              <span className="text-gray-500">Uptime: </span>
              <span>{Math.round(health.uptime_seconds)}s</span>
            </div>
            <div>
              <span className="text-gray-500">Version: </span>
              <span>{health.version}</span>
            </div>
          </div>
        </div>
      )}

      <h2 className="text-xl font-bold mb-4">LLM Providers</h2>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {providers.map((p) => (
          <div key={p.name} className="bg-white border rounded-xl p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-900 capitalize">{p.name}</h3>
              <span
                className={`text-xs px-2 py-0.5 rounded-full ${
                  p.available
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-600'
                }`}
              >
                {p.available ? 'Connected' : 'Not configured'}
              </span>
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 mb-1">Models</p>
              <div className="flex flex-wrap gap-1">
                {p.models.map((m) => (
                  <span
                    key={m}
                    className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded"
                  >
                    {m}
                  </span>
                ))}
                {p.models.length === 0 && (
                  <span className="text-xs text-gray-400">No models listed</span>
                )}
              </div>
            </div>
          </div>
        ))}

        {providers.length === 0 && (
          <div className="col-span-full text-center py-12 text-gray-400">
            <p>No providers configured. Add API keys to .env to enable providers.</p>
          </div>
        )}
      </div>
    </div>
  )
}
