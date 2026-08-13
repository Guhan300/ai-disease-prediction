import { Brain } from 'lucide-react'
import { motion } from 'motion/react'
import { formatChatTime } from '../../utils/format'
import { PredictionCard } from '../PredictionCard'
import { SafetyAlert } from '../SafetyAlert'

export function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const hasResult =
    Boolean(message.prediction?.top_predictions?.length) ||
    message.type === 'result'

  if (!isUser && hasResult) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35 }}
        className="flex items-start gap-3"
      >
        <div
          className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full"
          style={{
            background: 'rgba(45,212,191,0.12)',
            border: '1px solid rgba(45,212,191,0.22)',
          }}
        >
          <Brain size={13} className="text-teal-400" />
        </div>
        <div className="min-w-0 flex-1">
          {message.content && (
            <p className="mb-3 whitespace-pre-wrap text-sm leading-relaxed text-[rgba(228,232,242,0.78)]">
              {message.content}
            </p>
          )}
          <PredictionCard
            prediction={message.prediction}
            explanation={message.explanation}
            sources={message.sources}
          />
          <SafetyAlert safety={message.safety} />
          <p className="mt-2 font-mono text-[10px] text-white/20">
            {formatChatTime(message.created_at)}
          </p>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex items-end gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {isUser ? (
        <div
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-[rgba(228,232,242,0.5)]"
          style={{
            background: 'rgba(255,255,255,0.07)',
            border: '1px solid rgba(255,255,255,0.12)',
          }}
        >
          Y
        </div>
      ) : (
        <div
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full"
          style={{
            background: 'rgba(6,182,212,0.12)',
            border: '1px solid rgba(6,182,212,0.22)',
          }}
        >
          <Brain size={13} className="text-cyan-400" />
        </div>
      )}

      <div
        className="max-w-[76%] px-4 py-3 text-sm leading-relaxed"
        style={
          isUser
            ? {
                borderRadius: '1rem 1rem 0.25rem 1rem',
                background: 'rgba(6,182,212,0.10)',
                border: '1px solid rgba(6,182,212,0.18)',
                color: 'rgba(228,232,242,0.88)',
              }
            : {
                borderRadius: '1rem 1rem 1rem 0.25rem',
                background: '#0d1524',
                border: '1px solid rgba(255,255,255,0.07)',
                color: 'rgba(228,232,242,0.78)',
              }
        }
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!isUser && <SafetyAlert safety={message.safety} />}
        <p className="mt-1.5 font-mono text-[10px] text-white/20">
          {formatChatTime(message.created_at)}
        </p>
      </div>
    </motion.div>
  )
}
