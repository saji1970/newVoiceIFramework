import { create } from 'zustand'
import { api } from '../api/client'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

interface ChatState {
  messages: Message[]
  conversationId: string | null
  isLoading: boolean
  provider: string | null
  model: string | null
  systemPrompt: string
  error: string | null

  sendMessage: (content: string) => Promise<void>
  sendMessageStream: (content: string) => Promise<void>
  setProvider: (provider: string | null) => void
  setModel: (model: string | null) => void
  setSystemPrompt: (prompt: string) => void
  clearChat: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  conversationId: null,
  isLoading: false,
  provider: null,
  model: null,
  systemPrompt: 'You are a helpful assistant.',
  error: null,

  sendMessage: async (content: string) => {
    const { conversationId, provider, model, systemPrompt } = get()
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: Date.now(),
    }
    set((s) => ({ messages: [...s.messages, userMsg], isLoading: true, error: null }))

    try {
      const res = await api.chat({
        message: content,
        conversation_id: conversationId,
        provider,
        model,
        system_prompt: systemPrompt || undefined,
      })
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: res.response,
        timestamp: Date.now(),
      }
      set((s) => ({
        messages: [...s.messages, assistantMsg],
        conversationId: res.conversation_id,
        isLoading: false,
      }))
    } catch (err) {
      set({ isLoading: false, error: String(err) })
    }
  },

  sendMessageStream: async (content: string) => {
    const { conversationId, provider, model, systemPrompt } = get()
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: Date.now(),
    }
    const assistantMsg: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    }
    set((s) => ({
      messages: [...s.messages, userMsg, assistantMsg],
      isLoading: true,
      error: null,
    }))

    try {
      const res = await api.chatStream({
        message: content,
        conversation_id: conversationId,
        provider,
        model,
        system_prompt: systemPrompt || undefined,
      })
      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      if (!reader) throw new Error('No response body')

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
                set({ conversationId: data.conversation_id })
              } else if (data.type === 'chunk') {
                set((s) => {
                  const msgs = [...s.messages]
                  const last = msgs[msgs.length - 1]
                  if (last?.role === 'assistant') {
                    msgs[msgs.length - 1] = { ...last, content: last.content + data.content }
                  }
                  return { messages: msgs }
                })
              }
            } catch {
              // skip malformed lines
            }
          }
        }
      }
      set({ isLoading: false })
    } catch (err) {
      set({ isLoading: false, error: String(err) })
    }
  },

  setProvider: (provider) => set({ provider }),
  setModel: (model) => set({ model }),
  setSystemPrompt: (prompt) => set({ systemPrompt: prompt }),
  clearChat: () => set({ messages: [], conversationId: null, error: null }),
}))
