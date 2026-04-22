import type { VoiceIConfig, ChatMessage } from './types'
import { VoiceIClient } from './client'

const DEFAULT_STYLES = `
.voicei-widget {
  position: fixed;
  z-index: 10000;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
.voicei-widget.bottom-right { bottom: 20px; right: 20px; }
.voicei-widget.bottom-left { bottom: 20px; left: 20px; }
.voicei-widget.top-right { top: 20px; right: 20px; }
.voicei-widget.top-left { top: 20px; left: 20px; }

.voicei-toggle {
  width: 56px; height: 56px; border-radius: 28px;
  background: #2563eb; color: white; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  font-size: 24px; transition: transform 0.2s;
}
.voicei-toggle:hover { transform: scale(1.05); }

.voicei-panel {
  position: absolute; bottom: 70px; right: 0;
  width: 380px; height: 520px;
  background: white; border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.12);
  display: flex; flex-direction: column;
  overflow: hidden;
}
.voicei-panel.hidden { display: none; }

.voicei-header {
  padding: 16px; border-bottom: 1px solid #e5e7eb;
  font-weight: 600; font-size: 15px;
}

.voicei-messages {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 8px;
}

.voicei-msg {
  max-width: 80%; padding: 10px 14px; border-radius: 16px;
  font-size: 14px; line-height: 1.5; word-wrap: break-word;
}
.voicei-msg.user {
  align-self: flex-end; background: #2563eb; color: white;
  border-bottom-right-radius: 4px;
}
.voicei-msg.assistant {
  align-self: flex-start; background: #f3f4f6; color: #111827;
  border-bottom-left-radius: 4px;
}

.voicei-input-area {
  padding: 12px; border-top: 1px solid #e5e7eb;
  display: flex; gap: 8px;
}
.voicei-input {
  flex: 1; border: 1px solid #d1d5db; border-radius: 12px;
  padding: 10px 14px; font-size: 14px; outline: none;
  font-family: inherit;
}
.voicei-input:focus { border-color: #2563eb; box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }

.voicei-send {
  width: 40px; height: 40px; border-radius: 12px;
  background: #2563eb; color: white; border: none; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px;
}
.voicei-send:disabled { opacity: 0.5; cursor: not-allowed; }
`

export class VoiceIWidget {
  private config: VoiceIConfig
  private client: VoiceIClient
  private container: HTMLDivElement | null = null
  private panel: HTMLDivElement | null = null
  private messagesEl: HTMLDivElement | null = null
  private input: HTMLInputElement | null = null
  private isOpen = false
  private messages: ChatMessage[] = []
  private isLoading = false

  constructor(config: VoiceIConfig) {
    this.config = {
      position: 'bottom-right',
      theme: 'light',
      title: 'Chat',
      placeholder: 'Type a message...',
      enableVoice: false,
      ...config,
    }
    this.client = new VoiceIClient(config)
  }

  mount(targetEl?: HTMLElement) {
    // Inject styles
    const style = document.createElement('style')
    style.textContent = DEFAULT_STYLES
    document.head.appendChild(style)

    // Create widget container
    this.container = document.createElement('div')
    this.container.className = `voicei-widget ${this.config.position}`

    // Toggle button
    const toggle = document.createElement('button')
    toggle.className = 'voicei-toggle'
    toggle.innerHTML = '💬'
    toggle.onclick = () => this.toggle()

    // Chat panel
    this.panel = document.createElement('div')
    this.panel.className = 'voicei-panel hidden'
    this.panel.innerHTML = `
      <div class="voicei-header">${this.config.title}</div>
      <div class="voicei-messages"></div>
      <div class="voicei-input-area">
        <input class="voicei-input" placeholder="${this.config.placeholder}" />
        <button class="voicei-send">→</button>
      </div>
    `

    this.messagesEl = this.panel.querySelector('.voicei-messages')
    this.input = this.panel.querySelector('.voicei-input')
    const sendBtn = this.panel.querySelector('.voicei-send') as HTMLButtonElement

    this.input!.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.send()
    })
    sendBtn.addEventListener('click', () => this.send())

    this.container.appendChild(this.panel)
    this.container.appendChild(toggle)

    const target = targetEl || document.body
    target.appendChild(this.container)
  }

  toggle() {
    this.isOpen = !this.isOpen
    this.panel?.classList.toggle('hidden', !this.isOpen)
    if (this.isOpen) this.input?.focus()
  }

  private async send() {
    const text = this.input?.value.trim()
    if (!text || this.isLoading) return

    this.input!.value = ''
    this.addMessage('user', text)
    this.isLoading = true

    try {
      let response = ''
      this.addMessage('assistant', '')

      for await (const chunk of this.client.chatStream(text)) {
        response += chunk
        this.updateLastMessage(response)
      }
    } catch {
      // Fallback to non-streaming
      try {
        const res = await this.client.chat(text)
        this.updateLastMessage(res.response)
      } catch (err) {
        this.updateLastMessage('Sorry, something went wrong.')
      }
    }

    this.isLoading = false
  }

  private addMessage(role: 'user' | 'assistant', content: string) {
    this.messages.push({ role, content, timestamp: Date.now() })
    const div = document.createElement('div')
    div.className = `voicei-msg ${role}`
    div.textContent = content
    this.messagesEl?.appendChild(div)
    this.messagesEl!.scrollTop = this.messagesEl!.scrollHeight
  }

  private updateLastMessage(content: string) {
    if (this.messages.length === 0) return
    this.messages[this.messages.length - 1].content = content
    const lastEl = this.messagesEl?.lastElementChild as HTMLDivElement
    if (lastEl) {
      lastEl.textContent = content
      this.messagesEl!.scrollTop = this.messagesEl!.scrollHeight
    }
  }

  destroy() {
    this.container?.remove()
  }
}
