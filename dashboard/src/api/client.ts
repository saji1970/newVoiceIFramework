const API_BASE = '/api'

function buildHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const h: Record<string, string> = {
    'Content-Type': 'application/json',
    ...extra,
  }
  const key = import.meta.env.VITE_API_KEY
  if (key) {
    h['X-API-Key'] = key
  }
  return h
}

interface RequestOptions {
  method?: string
  body?: unknown
  headers?: Record<string, string>
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: buildHeaders(headers),
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

// Chat
export interface ChatRequest {
  message: string
  conversation_id?: string | null
  system_prompt?: string | null
  provider?: string | null
  model?: string | null
  temperature?: number
  max_tokens?: number
  stream?: boolean
}

export interface ChatResponse {
  response: string
  conversation_id: string
}

export const api = {
  // Chat
  chat: (req: ChatRequest) => request<ChatResponse>('/chat', { method: 'POST', body: req }),

  chatStream: (req: ChatRequest) => {
    return fetch(`${API_BASE}/chat/stream`, {
      method: 'POST',
      headers: buildHeaders(),
      body: JSON.stringify(req),
    })
  },

  getConversations: () => request<{ conversations: string[] }>('/conversations'),

  getConversation: (id: string) =>
    request<{ id: string; messages: Array<{ role: string; content: string; timestamp: number }> }>(
      `/conversations/${id}`
    ),

  // Providers
  getProviders: () =>
    request<{ providers: Array<{ name: string; available: boolean; models: string[] }> }>(
      '/providers'
    ),

  getProviderModels: (name: string) =>
    request<{ models: string[] }>(`/providers/${name}/models`),

  // Pipelines
  getPipelines: () =>
    request<{ pipelines: Array<{ id: string; name: string; description: string | null; version: string; enabled: boolean }> }>(
      '/pipelines'
    ),

  createPipeline: (data: { name: string; description?: string; config: object; version?: string }) =>
    request('/pipelines', { method: 'POST', body: data }),

  getPipeline: (id: string) => request(`/pipelines/${id}`),

  updatePipeline: (id: string, data: object) =>
    request(`/pipelines/${id}`, { method: 'PUT', body: data }),

  deletePipeline: (id: string) =>
    request(`/pipelines/${id}`, { method: 'DELETE' }),

  runPipeline: (id: string, input: object, variables?: object) =>
    request(`/pipelines/${id}/run`, { method: 'POST', body: { input, variables } }),

  // Voice
  getVoiceProviders: () =>
    request<{ stt: string[]; tts: Record<string, string[]> }>('/voice/providers'),

  // Admin
  getHealth: () => request<{ status: string; uptime_seconds: number; version: string }>('/health'),
}
