import { Handle, Position, type NodeProps } from '@xyflow/react'

export default function APINode({ data }: NodeProps) {
  return (
    <div className="bg-white border-2 border-green-400 rounded-lg shadow-sm min-w-[180px]">
      <div className="bg-green-50 px-3 py-1.5 rounded-t-md border-b border-green-200">
        <span className="text-xs font-semibold text-green-700">API</span>
      </div>
      <div className="p-3 space-y-1.5">
        <div className="text-xs text-gray-500">Method</div>
        <div className="text-sm font-medium">{(data as any).method || 'GET'}</div>
        <div className="text-xs text-gray-500 mt-1">URL</div>
        <div className="text-sm font-medium truncate max-w-[160px]">
          {(data as any).url || 'https://...'}
        </div>
      </div>
      <Handle type="target" position={Position.Top} className="!bg-green-500" />
      <Handle type="source" position={Position.Bottom} className="!bg-green-500" />
    </div>
  )
}
