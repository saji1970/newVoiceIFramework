import { useEffect, useRef } from 'react'
import { useVoiceStore } from '../../stores/voiceStore'

export default function Waveform() {
  const { analyser, mode } = useVoiceStore()
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animRef = useRef<number>(0)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !analyser) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)

    const draw = () => {
      animRef.current = requestAnimationFrame(draw)
      analyser.getByteFrequencyData(dataArray)

      ctx.fillStyle = '#f9fafb'
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      const barWidth = (canvas.width / bufferLength) * 2.5
      let x = 0

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height * 0.8
        const hue = mode === 'listening' ? 220 : mode === 'speaking' ? 150 : 0
        ctx.fillStyle = `hsl(${hue}, 80%, ${50 + (dataArray[i] / 255) * 20}%)`
        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight)
        x += barWidth + 1
      }
    }

    draw()
    return () => cancelAnimationFrame(animRef.current)
  }, [analyser, mode])

  return (
    <canvas
      ref={canvasRef}
      width={400}
      height={100}
      className="w-full h-24 rounded-lg bg-gray-50 border"
    />
  )
}
