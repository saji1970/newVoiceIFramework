import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, Play } from 'lucide-react'
import { usePipelineStore } from '../stores/pipelineStore'
import Modal from '../components/common/Modal'

export default function PipelinesPage() {
  const { pipelines, fetchPipelines, deletePipeline, isLoading } = usePipelineStore()
  const navigate = useNavigate()
  const [showCreate, setShowCreate] = useState(false)

  useEffect(() => {
    fetchPipelines()
  }, [fetchPipelines])

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Pipelines</h2>
        <div className="flex gap-2">
          <button
            onClick={() => navigate('/flow-builder')}
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm rounded-lg hover:bg-brand-700"
          >
            <Plus size={16} />
            Visual Builder
          </button>
        </div>
      </div>

      {pipelines.length === 0 && !isLoading && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg">No pipelines yet</p>
          <p className="text-sm mt-1">Create one using the Visual Builder or the API</p>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {pipelines.map((p) => (
          <div key={p.id} className="bg-white border rounded-xl p-4 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{p.name}</h3>
                <p className="text-sm text-gray-500 mt-0.5">{p.description || 'No description'}</p>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full ${p.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                {p.enabled ? 'Active' : 'Disabled'}
              </span>
            </div>
            <div className="flex items-center justify-between mt-4 pt-3 border-t">
              <span className="text-xs text-gray-400">v{p.version}</span>
              <div className="flex gap-1">
                <button
                  onClick={() => navigate(`/flow-builder/${p.id}`)}
                  className="p-1.5 text-gray-400 hover:text-brand-600 rounded"
                >
                  <Play size={14} />
                </button>
                <button
                  onClick={() => deletePipeline(p.id)}
                  className="p-1.5 text-gray-400 hover:text-red-500 rounded"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
