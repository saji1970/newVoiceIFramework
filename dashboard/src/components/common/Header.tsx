import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { api } from '../../api/client'

const titles: Record<string, string> = {
  '/chat': 'Chat',
  '/voice': 'Voice',
  '/pipelines': 'Pipelines',
  '/flow-builder': 'Flow Builder',
  '/providers': 'Providers',
}

type ApiState = 'checking' | 'ok' | 'error'

export default function Header() {
  const location = useLocation()
  const pathKey = Object.keys(titles).find(
    (p) => p !== '/' && (location.pathname === p || location.pathname.startsWith(p + '/'))
  )
  const title = (pathKey && titles[pathKey]) || 'VoiceI'
  const [apiState, setApiState] = useState<ApiState>('checking')
  const [version, setVersion] = useState<string | null>(null)

  useEffect(() => {
    let cancel = false
    ;(async () => {
      try {
        const h = await api.getHealth()
        if (!cancel) {
          setApiState('ok')
          setVersion(h.version)
        }
      } catch {
        if (!cancel) setApiState('error')
      }
    })()
    const t = setInterval(() => {
      api
        .getHealth()
        .then((h) => {
          if (!cancel) {
            setApiState('ok')
            setVersion(h.version)
          }
        })
        .catch(() => {
          if (!cancel) setApiState('error')
        })
    }, 30_000)
    return () => {
      cancel = true
      clearInterval(t)
    }
  }, [])

  return (
    <header className="h-14 border-b border-slate-200/80 bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/80 flex items-center justify-between px-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-800 tracking-tight">{title}</h2>
      <div className="flex items-center gap-3 text-xs">
        {version && (
          <span className="text-slate-500 font-mono" title="API version">
            API {version}
          </span>
        )}
        <span
          className={
            apiState === 'ok'
              ? 'inline-flex items-center gap-1.5 text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full font-medium ring-1 ring-emerald-600/10'
              : apiState === 'error'
                ? 'inline-flex items-center gap-1.5 text-amber-800 bg-amber-50 px-2.5 py-1 rounded-full font-medium ring-1 ring-amber-600/15'
                : 'inline-flex items-center gap-1.5 text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full'
          }
        >
          <span
            className={
              apiState === 'ok'
                ? 'w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse'
                : apiState === 'error'
                  ? 'w-1.5 h-1.5 bg-amber-500 rounded-full'
                  : 'w-1.5 h-1.5 bg-slate-400 rounded-full'
            }
          />
          {apiState === 'checking' && 'Checking…'}
          {apiState === 'ok' && 'API online'}
          {apiState === 'error' && 'API unreachable'}
        </span>
      </div>
    </header>
  )
}
