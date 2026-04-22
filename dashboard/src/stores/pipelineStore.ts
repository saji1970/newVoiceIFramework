import { create } from 'zustand'
import type { Node, Edge } from '@xyflow/react'
import { applyNodeChanges, applyEdgeChanges } from '@xyflow/react'
import type { NodeChange, EdgeChange } from '@xyflow/react'
import { api } from '../api/client'

interface Pipeline {
  id: string
  name: string
  description: string | null
  version: string
  enabled: boolean
}

interface PipelineState {
  pipelines: Pipeline[]
  currentPipeline: Pipeline | null
  nodes: Node[]
  edges: Edge[]
  isLoading: boolean
  error: string | null

  fetchPipelines: () => Promise<void>
  createPipeline: (name: string, config: object) => Promise<void>
  deletePipeline: (id: string) => Promise<void>
  setNodes: (nodes: Node[]) => void
  setEdges: (edges: Edge[]) => void
  onNodesChange: (changes: NodeChange[]) => void
  onEdgesChange: (changes: EdgeChange[]) => void
  addNode: (node: Node) => void
  removeNode: (nodeId: string) => void
  updateNodeData: (nodeId: string, key: string, value: unknown) => void
  setCurrentPipeline: (pipeline: Pipeline | null) => void
  clearCanvas: () => void
  exportConfig: () => object
}

export const usePipelineStore = create<PipelineState>((set, get) => ({
  pipelines: [],
  currentPipeline: null,
  nodes: [],
  edges: [],
  isLoading: false,
  error: null,

  fetchPipelines: async () => {
    set({ isLoading: true, error: null })
    try {
      const res = await api.getPipelines()
      set({ pipelines: res.pipelines, isLoading: false })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : String(err), isLoading: false })
    }
  },

  createPipeline: async (name: string, config: object) => {
    set({ isLoading: true, error: null })
    try {
      await api.createPipeline({ name, config })
      await get().fetchPipelines()
      set({ isLoading: false })
    } catch (err) {
      set({ error: err instanceof Error ? err.message : String(err), isLoading: false })
    }
  },

  deletePipeline: async (id: string) => {
    try {
      await api.deletePipeline(id)
      set((s) => ({ pipelines: s.pipelines.filter((p) => p.id !== id) }))
    } catch (err) {
      set({ error: err instanceof Error ? err.message : String(err) })
    }
  },

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),

  onNodesChange: (changes) => {
    set((s) => ({ nodes: applyNodeChanges(changes, s.nodes) }))
  },

  onEdgesChange: (changes) => {
    set((s) => ({ edges: applyEdgeChanges(changes, s.edges) }))
  },

  addNode: (node) => set((s) => ({ nodes: [...s.nodes, node] })),

  removeNode: (nodeId) =>
    set((s) => ({
      nodes: s.nodes.filter((n) => n.id !== nodeId),
      edges: s.edges.filter((e) => e.source !== nodeId && e.target !== nodeId),
    })),

  updateNodeData: (nodeId, key, value) =>
    set((s) => ({
      nodes: s.nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, [key]: value } } : n
      ),
    })),

  setCurrentPipeline: (pipeline) => set({ currentPipeline: pipeline }),

  clearCanvas: () => set({ nodes: [], edges: [], currentPipeline: null }),

  exportConfig: () => {
    const { nodes } = get()
    const pipelineNodes = nodes.map((node) => ({
      id: node.id,
      type: (node.data as Record<string, unknown>)?.nodeType || 'llm',
      ...Object.fromEntries(
        Object.entries(node.data as Record<string, unknown>).filter(
          ([k, v]) => !['label', 'nodeType'].includes(k) && v != null
        )
      ),
    }))
    return {
      name: 'exported_pipeline',
      version: '1.0',
      trigger: 'chat',
      nodes: pipelineNodes,
    }
  },
}))
