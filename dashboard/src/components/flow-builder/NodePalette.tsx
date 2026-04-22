import { DragEvent } from 'react'
import { Brain, Globe, Shuffle, GitBranch, Repeat, Wrench } from 'lucide-react'

const nodeTypes = [
  { type: 'llm', label: 'LLM', icon: Brain, color: 'purple' },
  { type: 'api', label: 'API Call', icon: Globe, color: 'green' },
  { type: 'transform', label: 'Transform', icon: Shuffle, color: 'orange' },
  { type: 'condition', label: 'Condition', icon: GitBranch, color: 'yellow' },
  { type: 'loop', label: 'Loop', icon: Repeat, color: 'blue' },
  { type: 'tool', label: 'Tool', icon: Wrench, color: 'gray' },
]

const colorClasses: Record<string, string> = {
  purple: 'border-purple-300 bg-purple-50 text-purple-700 hover:bg-purple-100',
  green: 'border-green-300 bg-green-50 text-green-700 hover:bg-green-100',
  orange: 'border-orange-300 bg-orange-50 text-orange-700 hover:bg-orange-100',
  yellow: 'border-yellow-300 bg-yellow-50 text-yellow-700 hover:bg-yellow-100',
  blue: 'border-blue-300 bg-blue-50 text-blue-700 hover:bg-blue-100',
  gray: 'border-gray-300 bg-gray-50 text-gray-700 hover:bg-gray-100',
}

export default function NodePalette() {
  const onDragStart = (event: DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="w-56 bg-white border-r p-4">
      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
        Node Types
      </h3>
      <div className="space-y-2">
        {nodeTypes.map(({ type, label, icon: Icon, color }) => (
          <div
            key={type}
            draggable
            onDragStart={(e) => onDragStart(e, type)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg border cursor-grab active:cursor-grabbing transition-colors ${colorClasses[color]}`}
          >
            <Icon size={16} />
            <span className="text-sm font-medium">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
