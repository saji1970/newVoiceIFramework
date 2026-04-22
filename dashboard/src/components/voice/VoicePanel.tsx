import { useVoiceStore } from '../../stores/voiceStore'
import Waveform from './Waveform'
import VoiceControls from './VoiceControls'

export default function VoicePanel() {
  const { transcript, response, error } = useVoiceStore()

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Waveform visualization */}
      <Waveform />

      {/* Controls */}
      <div className="flex justify-center">
        <VoiceControls />
      </div>

      {/* Transcript */}
      {transcript && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <p className="text-xs font-medium text-blue-600 mb-1">You said:</p>
          <p className="text-sm text-blue-900">{transcript}</p>
        </div>
      )}

      {/* Response */}
      {response && (
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
          <p className="text-xs font-medium text-gray-500 mb-1">Assistant:</p>
          <p className="text-sm text-gray-900">{response}</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-600">
          {error}
        </div>
      )}
    </div>
  )
}
