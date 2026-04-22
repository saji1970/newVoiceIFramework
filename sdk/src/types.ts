export interface VoiceIConfig {
  serverUrl: string
  apiKey?: string
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  theme?: 'light' | 'dark'
  provider?: string
  model?: string
  systemPrompt?: string
  enableVoice?: boolean
  title?: string
  placeholder?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export interface ChatResponse {
  response: string
  conversation_id: string
}
