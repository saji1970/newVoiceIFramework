export { VoiceIWidget } from './widget'
export { VoiceIClient } from './client'
export type { VoiceIConfig, ChatMessage, ChatResponse } from './types'

// Auto-init from script tag data attributes
if (typeof window !== 'undefined') {
  const script = document.currentScript as HTMLScriptElement | null
  if (script?.dataset.serverUrl) {
    const widget = new (await import('./widget')).VoiceIWidget({
      serverUrl: script.dataset.serverUrl,
      apiKey: script.dataset.apiKey,
      position: (script.dataset.position as any) || 'bottom-right',
      title: script.dataset.title || 'Chat',
    })
    widget.mount()
    ;(window as any).VoiceI = widget
  }
}
