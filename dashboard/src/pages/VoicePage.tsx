import VoicePanel from '../components/voice/VoicePanel'

export default function VoicePage() {
  return (
    <div className="p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Voice Interface</h2>
          <p className="text-gray-500 mt-1">
            Talk to the AI using your microphone. Real-time streaming or push-to-talk.
          </p>
        </div>
        <VoicePanel />
      </div>
    </div>
  )
}
