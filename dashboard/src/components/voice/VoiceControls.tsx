import { Mic, MicOff, Radio, Square } from 'lucide-react'
import { useVoiceStore } from '../../stores/voiceStore'
import clsx from 'clsx'

export default function VoiceControls() {
  const { mode, startStreaming, stopStreaming } = useVoiceStore()
  const isActive = mode !== 'idle'

  return (
    <div className="flex items-center gap-4">
      <button
        onClick={isActive ? stopStreaming : startStreaming}
        className={clsx(
          'flex items-center gap-2 px-6 py-3 rounded-full font-medium text-sm transition-all',
          isActive
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-brand-600 hover:bg-brand-700 text-white'
        )}
      >
        {isActive ? (
          <>
            <Square size={18} />
            Stop
          </>
        ) : (
          <>
            <Radio size={18} />
            Start Streaming
          </>
        )}
      </button>

      <div className="flex items-center gap-2 text-sm text-gray-500">
        {mode === 'idle' && <MicOff size={16} />}
        {mode === 'listening' && (
          <span className="flex items-center gap-1.5 text-blue-600">
            <Mic size={16} className="animate-pulse" />
            Listening...
          </span>
        )}
        {mode === 'processing' && (
          <span className="text-yellow-600">Processing...</span>
        )}
        {mode === 'speaking' && (
          <span className="text-green-600">Speaking...</span>
        )}
      </div>
    </div>
  )
}
