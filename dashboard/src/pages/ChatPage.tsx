import { useEffect, useState } from 'react'
import ChatWindow from '../components/chat/ChatWindow'
import { useChatStore } from '../stores/chatStore'
import { api } from '../api/client'

export default function ChatPage() {
  const { provider, model, setProvider, setModel, systemPrompt, setSystemPrompt, clearChat } = useChatStore()
  const [providers, setProviders] = useState<Array<{ name: string; models: string[] }>>([])
  const [showSettings, setShowSettings] = useState(false)

  useEffect(() => {
    api.getProviders().then((res) => setProviders(res.providers)).catch(() => {})
  }, [])

  const currentProvider = providers.find((p) => p.name === provider)

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="flex items-center gap-3 px-4 py-2 border-b bg-gray-50">
        <select
          className="text-sm border rounded-lg px-3 py-1.5"
          value={provider || ''}
          onChange={(e) => {
            setProvider(e.target.value || null)
            setModel(null)
          }}
        >
          <option value="">Default Provider</option>
          {providers.map((p) => (
            <option key={p.name} value={p.name}>
              {p.name}
            </option>
          ))}
        </select>

        <select
          className="text-sm border rounded-lg px-3 py-1.5"
          value={model || ''}
          onChange={(e) => setModel(e.target.value || null)}
        >
          <option value="">Default Model</option>
          {(currentProvider?.models || []).map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>

        <button
          className="text-sm text-gray-500 hover:text-gray-700 ml-auto"
          onClick={() => setShowSettings(!showSettings)}
        >
          Settings
        </button>
        <button
          className="text-sm text-red-500 hover:text-red-700"
          onClick={clearChat}
        >
          Clear
        </button>
      </div>

      {/* Settings panel */}
      {showSettings && (
        <div className="px-4 py-3 border-b bg-gray-50">
          <label className="text-xs font-medium text-gray-500 block mb-1">System Prompt</label>
          <textarea
            className="w-full text-sm border rounded-lg px-3 py-2 max-w-2xl"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={2}
          />
        </div>
      )}

      {/* Chat area */}
      <div className="flex-1 overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  )
}
