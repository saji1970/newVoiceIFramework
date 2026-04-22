import { useCallback, useRef, useState, DragEvent } from 'react'
import {
  ReactFlow,
  Controls,
  Background,
  BackgroundVariant,
  addEdge,
  type Node,
  type OnConnect,
  type ReactFlowInstance,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import LLMNode from './nodes/LLMNode'
import APINode from './nodes/APINode'
import TransformNode from './nodes/TransformNode'
import ConditionNode from './nodes/ConditionNode'
import NodePalette from './NodePalette'
import PropertiesPanel from './PropertiesPanel'
import { usePipelineStore } from '../../stores/pipelineStore'
import { api } from '../../api/client'

const customNodeTypes = {
  llmNode: LLMNode,
  apiNode: APINode,
  transformNode: TransformNode,
  conditionNode: ConditionNode,
}

const nodeTypeMapping: Record<string, string> = {
  llm: 'llmNode',
  api: 'apiNode',
  transform: 'transformNode',
  condition: 'conditionNode',
  loop: 'default',
  tool: 'default',
}

let nodeIdCounter = 0
const getNodeId = () => `node_${++nodeIdCounter}`

export default function FlowCanvas() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    setEdges,
    addNode,
    removeNode,
    exportConfig,
    currentPipeline,
  } = usePipelineStore()

  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [saveStatus, setSaveStatus] = useState<string | null>(null)
  const reactFlowRef = useRef<ReactFlowInstance | null>(null)

  const onConnect: OnConnect = useCallback(
    (params) => setEdges(addEdge(params, usePipelineStore.getState().edges)),
    [setEdges]
  )

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    setSelectedNode(node)
  }, [])

  const onPaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  const onDragOver = useCallback((event: DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: DragEvent) => {
      event.preventDefault()
      const type = event.dataTransfer.getData('application/reactflow')
      if (!type || !reactFlowRef.current) return

      const reactFlowType = nodeTypeMapping[type] || 'default'
      const id = getNodeId()

      const position = reactFlowRef.current.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      })

      const newNode: Node = {
        id,
        type: reactFlowType,
        position,
        data: {
          label: `${type} node`,
          nodeType: type,
          provider: type === 'llm' ? 'openai' : undefined,
          model: type === 'llm' ? 'gpt-4o-mini' : undefined,
          method: type === 'api' ? 'GET' : undefined,
          template: type === 'transform' ? '{{input}}' : undefined,
          branches: type === 'condition' ? {} : undefined,
        },
      }
      addNode(newNode)
    },
    [addNode]
  )

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if ((event.key === 'Delete' || event.key === 'Backspace') && selectedNode) {
        // Don't delete if user is typing in an input
        if ((event.target as HTMLElement).tagName === 'INPUT' || (event.target as HTMLElement).tagName === 'TEXTAREA') return
        removeNode(selectedNode.id)
        setSelectedNode(null)
      }
    },
    [selectedNode, removeNode]
  )

  const handleExport = () => {
    const config = exportConfig()
    const json = JSON.stringify(config, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${currentPipeline?.name || 'pipeline'}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleSave = async () => {
    const config = exportConfig()
    const name = currentPipeline?.name || 'Untitled Pipeline'
    setSaveStatus('Saving...')
    try {
      if (currentPipeline) {
        await api.updatePipeline(currentPipeline.id, { name, config })
      } else {
        await api.createPipeline({ name, config })
      }
      setSaveStatus('Saved')
      setTimeout(() => setSaveStatus(null), 2000)
    } catch {
      setSaveStatus('Save failed')
      setTimeout(() => setSaveStatus(null), 3000)
    }
  }

  return (
    <div className="flex h-full" onKeyDown={handleKeyDown} tabIndex={0}>
      <NodePalette />
      <div className="flex-1 relative">
        <div className="absolute top-3 right-3 z-10 flex gap-2">
          {saveStatus && (
            <span className="px-3 py-2 text-sm text-gray-600 bg-white rounded-lg shadow-sm border">
              {saveStatus}
            </span>
          )}
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 shadow-sm"
          >
            Save Pipeline
          </button>
          <button
            onClick={handleExport}
            className="px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700 shadow-sm"
          >
            Export JSON
          </button>
        </div>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          onDragOver={onDragOver}
          onDrop={onDrop}
          onInit={(instance) => { reactFlowRef.current = instance }}
          nodeTypes={customNodeTypes}
          fitView
          deleteKeyCode={null}
        >
          <Controls />
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
        </ReactFlow>
      </div>
      <PropertiesPanel selectedNode={selectedNode} onDeleteNode={(id) => { removeNode(id); setSelectedNode(null) }} />
    </div>
  )
}
