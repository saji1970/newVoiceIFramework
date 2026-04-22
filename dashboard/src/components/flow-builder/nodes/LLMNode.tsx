import { Handle, Position, type NodeProps } from '@xyflow/react'

export default function LLMNode({ data }: NodeProps) {
  return (
    <div className="bg-white border-2 border-purple-400 rounded-lg shadow-sm min-w-[180px]">
      <div className="bg-purple-50 px-3 py-1.5 rounded-t-md border-b border-purple-200">
        <span className="text-xs font-semibold text-purple-700">LLM</span>
      </div>
      <div className="p-3 space-y-1.5">
        <div className="text-xs text-gray-500">Provider</div>
        <div className="text-sm font-medium">{(data as any).provider || 'openai'}</div>
        <div className="text-xs text-gray-500 mt-1">Model</div>
        <div className="text-sm font-medium">{(data as any).model || 'gpt-4o-mini'}</div>
      </div>
      <Handle type="target" position={Position.Top} className="!bg-purple-500" />
      <Handle type="source" position={Position.Bottom} className="!bg-purple-500" />
    </div>
  )
}
