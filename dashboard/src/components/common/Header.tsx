import { useLocation } from 'react-router-dom'

const titles: Record<string, string> = {
  '/chat': 'Chat',
  '/voice': 'Voice',
  '/pipelines': 'Pipelines',
  '/flow-builder': 'Flow Builder',
  '/providers': 'Providers',
}

export default function Header() {
  const location = useLocation()
  const title = titles[location.pathname] || 'VoiceI'

  return (
    <header className="h-14 border-b border-gray-200 bg-white flex items-center justify-between px-6">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="flex items-center gap-3">
        <span className="inline-flex items-center gap-1.5 text-xs text-green-600 bg-green-50 px-2 py-1 rounded-full">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
          Connected
        </span>
      </div>
    </header>
  )
}
