import type { VoiceIConfig, ChatMessage, ChatResponse } from './types'

export class VoiceIClient {
  private serverUrl: string
  private apiKey?: string
  private conversationId: string | null = null
  private provider?: string
  private model?: string
  private systemPrompt?: string

  constructor(config: VoiceIConfig) {
    this.serverUrl = config.serverUrl.replace(/\/$/, '')
    this.apiKey = config.apiKey
    this.provider = config.provider
    this.model = config.model
    this.systemPrompt = config.systemPrompt
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { 'Content-Type': 'application/json' }
    if (this.apiKey) h['X-API-Key'] = this.apiKey
    return h
  }

  async chat(message: string): Promise<ChatResponse> {
    const res = await fetch(`${this.serverUrl}/api/chat`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({
        message,
        conversation_id: this.conversationId,
        provider: this.provider,
        model: this.model,
        system_prompt: this.systemPrompt,
      }),
    })
    if (!res.ok) throw new Error(`Chat failed: ${res.status}`)
    const data: ChatResponse = await res.json()
    this.conversationId = data.conversation_id
    return data
  }

  async *chatStream(message: string): AsyncGenerator<string> {
    const res = await fetch(`${this.serverUrl}/api/chat/stream`, {
      method: 'POST',
      headers: this.headers(),
      body: JSON.stringify({
        message,
        conversation_id: this.conversationId,
        provider: this.provider,
        model: this.model,
        system_prompt: this.systemPrompt,
      }),
    })
    if (!res.ok) throw new Error(`Stream failed: ${res.status}`)

    const reader = res.body?.getReader()
    if (!reader) return

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            if (data.type === 'start') {
              this.conversationId = data.conversation_id
            } else if (data.type === 'chunk') {
              yield data.content
            }
          } catch {
            // skip
          }
        }
      }
    }
  }

  resetConversation() {
    this.conversationId = null
  }
}
