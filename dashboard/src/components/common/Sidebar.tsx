import { NavLink } from 'react-router-dom'
import { MessageSquare, Mic, GitBranch, Workflow, Settings } from 'lucide-react'
import clsx from 'clsx'

const navItems = [
  { to: '/chat', label: 'Chat', icon: MessageSquare },
  { to: '/voice', label: 'Voice', icon: Mic },
  { to: '/pipelines', label: 'Pipelines', icon: Workflow },
  { to: '/flow-builder', label: 'Flow Builder', icon: GitBranch },
  { to: '/providers', label: 'Providers', icon: Settings },
]

export default function Sidebar() {
  return (
    <aside className="w-60 bg-gray-900 text-white flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-xl font-bold tracking-tight">
          <span className="text-brand-400">Voice</span>I
        </h1>
        <p className="text-xs text-gray-400 mt-0.5">AI Framework</p>
      </div>
      <nav className="flex-1 p-2 space-y-0.5">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-brand-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              )
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500">
        v0.1.0
      </div>
    </aside>
  )
}
