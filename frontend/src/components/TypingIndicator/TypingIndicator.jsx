import { Brain } from 'lucide-react'
import { motion } from 'motion/react'

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 4 }}
      transition={{ duration: 0.2 }}
      className="flex items-end gap-3"
      aria-label="Assistant is typing"
    >
      <div
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full"
        style={{
          background: 'rgba(6,182,212,0.12)',
          border: '1px solid rgba(6,182,212,0.22)',
        }}
      >
        <Brain size={13} className="text-cyan-400" />
      </div>
      <div
        className="rounded-2xl rounded-bl-sm px-4 py-3.5"
        style={{
          background: '#0d1524',
          border: '1px solid rgba(255,255,255,0.07)',
        }}
      >
        <div className="flex items-center gap-1.5">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="h-1.5 w-1.5 rounded-full bg-white/30"
              animate={{ opacity: [0.25, 0.9, 0.25], y: [0, -2.5, 0] }}
              transition={{
                duration: 1.3,
                repeat: Infinity,
                delay: i * 0.18,
                ease: 'easeInOut',
              }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  )
}
