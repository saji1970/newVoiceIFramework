import { useEffect, useRef } from 'react'
import { useChatStore } from '../../stores/chatStore'
import MessageBubble from './MessageBubble'
import InputBar from './InputBar'

export default function ChatWindow() {
  const { messages, isLoading, error, sendMessageStream, clearChat } = useChatStore()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-400 mt-20">
              <p className="text-4xl mb-4">💬</p>
              <p className="text-lg font-medium">Start a conversation</p>
              <p className="text-sm mt-1">Send a message to begin chatting with an AI model</p>
            </div>
          )}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          {error && (
            <div className="text-red-500 text-sm bg-red-50 rounded-lg p-3">{error}</div>
          )}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Input */}
      <InputBar onSend={sendMessageStream} disabled={isLoading} />
    </div>
  )
}
