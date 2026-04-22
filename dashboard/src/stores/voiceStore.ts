import { create } from 'zustand'

type VoiceMode = 'idle' | 'listening' | 'processing' | 'speaking'

interface VoiceState {
  mode: VoiceMode
  transcript: string
  response: string
  error: string | null
  ws: WebSocket | null
  mediaRecorder: MediaRecorder | null
  audioContext: AudioContext | null
  analyser: AnalyserNode | null

  startStreaming: () => Promise<void>
  stopStreaming: () => void
  startRecording: () => Promise<void>
  stopRecording: () => Promise<Blob>
  reset: () => void
}

export const useVoiceStore = create<VoiceState>((set, get) => ({
  mode: 'idle',
  transcript: '',
  response: '',
  error: null,
  ws: null,
  mediaRecorder: null,
  audioContext: null,
  analyser: null,

  startStreaming: async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const audioContext = new AudioContext({ sampleRate: 16000 })
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)

      const wsUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/voice/stream`
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        set({ mode: 'listening' })
        // Start sending audio chunks
        const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' })
        recorder.ondataavailable = (e) => {
          if (e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
            ws.send(e.data)
          }
        }
        recorder.start(250) // Send chunks every 250ms
        set({ mediaRecorder: recorder })
      }

      ws.onmessage = (event) => {
        if (typeof event.data === 'string') {
          const msg = JSON.parse(event.data)
          switch (msg.type) {
            case 'transcript':
              set({ transcript: msg.text, mode: msg.final ? 'processing' : 'listening' })
              break
            case 'response_text':
              set({ response: msg.text })
              break
            case 'response_end':
              set({ mode: 'speaking' })
              break
            case 'audio_end':
              set({ mode: 'listening' })
              break
            case 'error':
              set({ error: msg.message, mode: 'idle' })
              break
          }
        } else if (event.data instanceof Blob) {
          // Play audio response
          const audio = new Audio(URL.createObjectURL(event.data))
          audio.play()
        }
      }

      ws.onclose = () => set({ mode: 'idle', ws: null })
      ws.onerror = () => set({ error: 'WebSocket error', mode: 'idle' })

      set({ ws, audioContext, analyser })
    } catch (err) {
      set({ error: String(err), mode: 'idle' })
    }
  },

  stopStreaming: () => {
    const { ws, mediaRecorder, audioContext } = get()
    mediaRecorder?.stop()
    ws?.close()
    audioContext?.close()
    set({ mode: 'idle', ws: null, mediaRecorder: null, audioContext: null, analyser: null })
  },

  startRecording: async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const audioContext = new AudioContext()
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 256
      const source = audioContext.createMediaStreamSource(stream)
      source.connect(analyser)

      const recorder = new MediaRecorder(stream)
      const chunks: Blob[] = []
      recorder.ondataavailable = (e) => chunks.push(e.data)
      recorder.start()

      set({ mode: 'listening', mediaRecorder: recorder, audioContext, analyser })
    } catch (err) {
      set({ error: String(err) })
    }
  },

  stopRecording: async () => {
    const { mediaRecorder, audioContext } = get()
    return new Promise<Blob>((resolve) => {
      if (!mediaRecorder) {
        resolve(new Blob())
        return
      }
      const chunks: Blob[] = []
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = () => {
        resolve(new Blob(chunks, { type: 'audio/webm' }))
        audioContext?.close()
        set({ mode: 'processing', mediaRecorder: null, audioContext: null, analyser: null })
      }
      mediaRecorder.stop()
    })
  },

  reset: () => {
    const { ws, mediaRecorder, audioContext } = get()
    mediaRecorder?.stop()
    ws?.close()
    audioContext?.close()
    set({
      mode: 'idle',
      transcript: '',
      response: '',
      error: null,
      ws: null,
      mediaRecorder: null,
      audioContext: null,
      analyser: null,
    })
  },
}))
