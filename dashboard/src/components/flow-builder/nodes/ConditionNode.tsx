import { Handle, Position, type NodeProps } from '@xyflow/react'

export default function ConditionNode({ data }: NodeProps) {
  const branches = (data as any).branches || {}
  return (
    <div className="bg-white border-2 border-yellow-400 rounded-lg shadow-sm min-w-[180px]">
      <div className="bg-yellow-50 px-3 py-1.5 rounded-t-md border-b border-yellow-200">
        <span className="text-xs font-semibold text-yellow-700">Condition</span>
      </div>
      <div className="p-3">
        <div className="text-xs text-gray-500">Branches</div>
        <div className="mt-1 space-y-0.5">
          {Object.keys(branches).map((key) => (
            <div key={key} className="text-xs bg-yellow-50 px-2 py-0.5 rounded">
              {key}
            </div>
          ))}
          {Object.keys(branches).length === 0 && (
            <div className="text-xs text-gray-400">No branches</div>
          )}
        </div>
      </div>
      <Handle type="target" position={Position.Top} className="!bg-yellow-500" />
      <Handle type="source" position={Position.Bottom} className="!bg-yellow-500" />
    </div>
  )
}
