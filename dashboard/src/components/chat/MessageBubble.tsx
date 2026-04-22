import clsx from 'clsx'
import type { Message } from '../../stores/chatStore'

interface Props {
  message: Message
}

export default function MessageBubble({ message }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
          isUser
            ? 'bg-brand-600 text-white rounded-br-md'
            : 'bg-gray-100 text-gray-900 rounded-bl-md'
        )}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        {message.content === '' && (
          <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse rounded-sm" />
        )}
      </div>
    </div>
  )
}
