import { useEffect, useRef } from 'react'
import { AnimatePresence } from 'motion/react'
import { MessageBubble } from '../MessageBubble'
import { TypingIndicator } from '../TypingIndicator'
import { EmptyState } from '../EmptyState'

export function ChatWindow({
  messages,
  isTyping,
  error,
  showEmptyState,
  onSuggestion,
}) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  if (showEmptyState) {
    return (
      <div className="chat-scroll min-h-0 flex-1 overflow-y-auto">
        <EmptyState onSuggestion={onSuggestion} />
      </div>
    )
  }

  return (
    <div className="chat-scroll min-h-0 flex-1 overflow-y-auto">
      <div className="mx-auto max-w-[680px] space-y-5 px-4 py-6 sm:px-6">
        {messages.map((message) => (
          <MessageBubble
            key={message.id || `${message.role}-${message.created_at}`}
            message={message}
          />
        ))}

        <AnimatePresence>{isTyping ? <TypingIndicator /> : null}</AnimatePresence>

        {error && (
          <div
            className="rounded-xl px-4 py-3 text-sm text-rose-200"
            style={{
              background: 'rgba(239,68,68,0.08)',
              border: '1px solid rgba(239,68,68,0.25)',
            }}
            role="alert"
          >
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
