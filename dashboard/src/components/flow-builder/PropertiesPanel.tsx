import { useCallback } from 'react'
import type { Node } from '@xyflow/react'
import { Trash2 } from 'lucide-react'
import { usePipelineStore } from '../../stores/pipelineStore'

interface Props {
  selectedNode: Node | null
  onDeleteNode: (id: string) => void
}

export default function PropertiesPanel({ selectedNode, onDeleteNode }: Props) {
  const { updateNodeData } = usePipelineStore()

  const handleUpdate = useCallback(
    (key: string, value: string) => {
      if (!selectedNode) return
      updateNodeData(selectedNode.id, key, value)
    },
    [selectedNode, updateNodeData]
  )

  if (!selectedNode) {
    return (
      <div className="w-72 bg-white border-l p-4">
        <p className="text-sm text-gray-400 text-center mt-8">
          Select a node to edit its properties
        </p>
      </div>
    )
  }

  const data = selectedNode.data as Record<string, any>
  const nodeType = data.nodeType || selectedNode.type

  return (
    <div className="w-72 bg-white border-l p-4 overflow-auto">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-700">Node Properties</h3>
        <button
          onClick={() => onDeleteNode(selectedNode.id)}
          className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors"
          title="Delete node"
        >
          <Trash2 size={14} />
        </button>
      </div>

      <div className="space-y-3">
        <div>
          <label className="text-xs font-medium text-gray-500">ID</label>
          <input
            className="w-full mt-1 text-sm border rounded-lg px-3 py-2 bg-gray-50"
            value={selectedNode.id}
            disabled
          />
        </div>

        <div>
          <label className="text-xs font-medium text-gray-500">Type</label>
          <input
            className="w-full mt-1 text-sm border rounded-lg px-3 py-2 bg-gray-50"
            value={nodeType || ''}
            disabled
          />
        </div>

        {(nodeType === 'llm' || nodeType === 'llmNode') && (
          <>
            <div>
              <label className="text-xs font-medium text-gray-500">Provider</label>
              <select
                className="w-full mt-1 text-sm border rounded-lg px-3 py-2"
                value={data.provider || 'openai'}
                onChange={(e) => handleUpdate('provider', e.target.value)}
              >
                <option value="openai">OpenAI</option>
                <option value="anthropic">Anthropic</option>
                <option value="ollama">Ollama</option>
                <option value="google">Google</option>
                <option value="mistral">Mistral</option>
                <option value="cohere">Cohere</option>
              </select>
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500">Model</label>
              <input
                className="w-full mt-1 text-sm border rounded-lg px-3 py-2"
                value={data.model || ''}
                onChange={(e) => handleUpdate('model', e.target.value)}
                placeholder="gpt-4o-mini"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500">Prompt</label>
              <textarea
                className="w-full mt-1 text-sm border rounded-lg px-3 py-2 min-h-[80px]"
                value={data.prompt || ''}
                onChange={(e) => handleUpdate('prompt', e.target.value)}
                placeholder="Enter prompt template..."
              />
            </div>
          </>
        )}

        {(nodeType === 'api' || nodeType === 'apiNode') && (
          <>
            <div>
              <label className="text-xs font-medium text-gray-500">URL</label>
              <input
                className="w-full mt-1 text-sm border rounded-lg px-3 py-2"
                value={data.url || ''}
                onChange={(e) => handleUpdate('url', e.target.value)}
                placeholder="https://api.example.com/..."
              />
            </div>
            <div>
              <label className="text-xs font-medium text-gray-500">Method</label>
              <select
                className="w-full mt-1 text-sm border rounded-lg px-3 py-2"
                value={data.method || 'GET'}
                onChange={(e) => handleUpdate('method', e.target.value)}
              >
                <option>GET</option>
                <option>POST</option>
                <option>PUT</option>
                <option>DELETE</option>
              </select>
            </div>
          </>
        )}

        {(nodeType === 'transform' || nodeType === 'transformNode') && (
          <div>
            <label className="text-xs font-medium text-gray-500">Template</label>
            <textarea
              className="w-full mt-1 text-sm border rounded-lg px-3 py-2 font-mono min-h-[80px]"
              value={data.template || ''}
              onChange={(e) => handleUpdate('template', e.target.value)}
              placeholder="{{input}}"
            />
          </div>
        )}

        {(nodeType === 'condition' || nodeType === 'conditionNode') && (
          <div>
            <label className="text-xs font-medium text-gray-500">Input Expression</label>
            <input
              className="w-full mt-1 text-sm border rounded-lg px-3 py-2"
              value={data.input || ''}
              onChange={(e) => handleUpdate('input', e.target.value)}
              placeholder="{{variable}}"
            />
          </div>
        )}
      </div>
    </div>
  )
}
