import { Brain } from 'lucide-react'
import { motion } from 'motion/react'

const SUGGESTIONS = [
  'Fever & headache',
  'Skin irritation',
  'Chest tightness',
  'Digestive pain',
  'Joint stiffness',
  'Persistent fatigue',
]

export function EmptyState({ onSuggestion }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-7 px-6 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.94 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.35 }}
        className="space-y-1"
      >
        <div
          className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl"
          style={{
            background: 'rgba(6,182,212,0.09)',
            border: '1px solid rgba(6,182,212,0.18)',
            boxShadow: '0 0 32px rgba(6,182,212,0.08)',
          }}
        >
          <Brain size={26} className="text-cyan-400" />
        </div>
        <h2 className="text-xl font-semibold text-[rgba(228,232,242,0.88)]">
          How can I help you today?
        </h2>
        <p className="mx-auto max-w-xs text-sm leading-relaxed text-[rgba(228,232,242,0.36)]">
          Describe your symptoms and MedAI will gather details, then run the trained ML
          model for educational risk estimates.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.1 }}
        className="flex max-w-md flex-wrap justify-center gap-2"
      >
        {SUGGESTIONS.map((label, i) => (
          <motion.button
            key={label}
            type="button"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: 0.12 + i * 0.05 }}
            onClick={() => onSuggestion?.(label)}
            className="rounded-full px-3.5 py-2 text-xs transition"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.08)',
              color: 'rgba(228,232,242,0.45)',
            }}
          >
            {label}
          </motion.button>
        ))}
      </motion.div>

      <p className="font-mono text-[10px] text-white/20">
        Tap a suggestion to send it as a real chat message · Or type below
      </p>
    </div>
  )
}
