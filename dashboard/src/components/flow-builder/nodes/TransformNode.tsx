import { Handle, Position, type NodeProps } from '@xyflow/react'

export default function TransformNode({ data }: NodeProps) {
  return (
    <div className="bg-white border-2 border-orange-400 rounded-lg shadow-sm min-w-[180px]">
      <div className="bg-orange-50 px-3 py-1.5 rounded-t-md border-b border-orange-200">
        <span className="text-xs font-semibold text-orange-700">Transform</span>
      </div>
      <div className="p-3">
        <div className="text-xs text-gray-500">Template</div>
        <div className="text-sm font-mono text-gray-700 truncate max-w-[160px]">
          {(data as any).template || '{{input}}'}
        </div>
      </div>
      <Handle type="target" position={Position.Top} className="!bg-orange-500" />
      <Handle type="source" position={Position.Bottom} className="!bg-orange-500" />
    </div>
  )
}
