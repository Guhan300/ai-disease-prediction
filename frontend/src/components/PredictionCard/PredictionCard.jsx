import { AlertTriangle, CheckCircle2, FileText } from 'lucide-react'
import { motion } from 'motion/react'
import clsx from 'clsx'

function ScoreBar({ score, colorClass }) {
  const pct = Math.max(0, Math.min(100, Math.round(Number(score) * 100)))
  return (
    <div
      className="h-1.5 w-full overflow-hidden rounded-full"
      style={{ background: 'rgba(255,255,255,0.08)' }}
    >
      <motion.div
        className={clsx('h-full rounded-full', colorClass)}
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ duration: 1.0, ease: 'easeOut', delay: 0.2 }}
      />
    </div>
  )
}

const BAR_COLORS = ['bg-teal-400', 'bg-cyan-400', 'bg-sky-400']

export function PredictionCard({ prediction, explanation, sources }) {
  const items = prediction?.top_predictions || []
  const features = explanation?.important_features || []
  const sourceList = sources || []

  if (!items.length) return null

  const primary = items[0]
  const others = items.slice(1)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: 'easeOut' }}
      className="w-full overflow-hidden rounded-2xl"
      style={{
        border: '1px solid rgba(255,255,255,0.08)',
        background: '#0d1524',
      }}
    >
      <div
        className="flex items-center gap-3 border-b px-5 py-4"
        style={{
          borderColor: 'rgba(255,255,255,0.06)',
          background: 'rgba(255,255,255,0.015)',
        }}
      >
        <div
          className="flex h-8 w-8 items-center justify-center rounded-full"
          style={{
            background: 'rgba(45,212,191,0.12)',
            border: '1px solid rgba(45,212,191,0.22)',
          }}
        >
          <CheckCircle2 size={15} className="text-teal-400" />
        </div>
        <div>
          <div className="text-sm font-semibold text-[rgba(228,232,242,0.9)]">
            Assessment Complete
          </div>
          <div className="mt-0.5 font-mono text-[11px] tracking-wide text-[rgba(228,232,242,0.35)]">
            {items.length} model-ranked possible condition
            {items.length === 1 ? '' : 's'}
          </div>
        </div>
      </div>

      <div className="space-y-6 p-5">
        <div>
          <div className="mb-3 font-mono text-[10px] uppercase tracking-[0.14em] text-[rgba(228,232,242,0.3)]">
            Primary assessment
          </div>
          <div
            className="rounded-xl p-4"
            style={{
              background: 'rgba(45,212,191,0.06)',
              border: '1px solid rgba(45,212,191,0.16)',
            }}
          >
            <div className="mb-3 flex items-start justify-between gap-3">
              <div>
                <div className="text-lg font-bold leading-none text-[rgba(228,232,242,0.92)]">
                  {primary.condition}
                </div>
                <div className="mt-1 font-mono text-[11px] text-[rgba(228,232,242,0.35)]">
                  Top model prediction · model score
                </div>
              </div>
              <div className="font-mono text-3xl font-bold leading-none text-teal-400">
                {Math.round(primary.score * 100)}%
              </div>
            </div>
            <ScoreBar score={primary.score} colorClass={BAR_COLORS[0]} />
          </div>
        </div>

        {others.length > 0 && (
          <div>
            <div className="mb-3 font-mono text-[10px] uppercase tracking-[0.14em] text-[rgba(228,232,242,0.3)]">
              Other considerations
            </div>
            <div className="space-y-3.5">
              {others.map((item, index) => (
                <div key={item.condition}>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="text-sm text-[rgba(228,232,242,0.65)]">
                      {item.condition}
                    </span>
                    <span className="font-mono text-sm text-[rgba(228,232,242,0.4)]">
                      {Math.round(item.score * 100)}%
                    </span>
                  </div>
                  <ScoreBar
                    score={item.score}
                    colorClass={BAR_COLORS[(index + 1) % BAR_COLORS.length]}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {features.length > 0 && (
          <div>
            <div className="mb-3 font-mono text-[10px] uppercase tracking-[0.14em] text-[rgba(228,232,242,0.3)]">
              Why this result?
            </div>
            <div className="flex flex-wrap gap-2">
              {features.map((feat) => (
                <span
                  key={`${feat.feature}-${feat.impact}`}
                  className="rounded-full px-2.5 py-1 font-mono text-[11px]"
                  style={{
                    background: 'rgba(255,255,255,0.05)',
                    border: '1px solid rgba(255,255,255,0.10)',
                    color: 'rgba(228,232,242,0.55)',
                  }}
                >
                  {feat.feature}
                  {feat.impact ? ` · ${feat.impact}` : ''}
                </span>
              ))}
            </div>
          </div>
        )}

        {sourceList.length > 0 && (
          <div>
            <div className="mb-3 font-mono text-[10px] uppercase tracking-[0.14em] text-[rgba(228,232,242,0.3)]">
              Knowledge sources
            </div>
            <ul className="space-y-2">
              {sourceList.map((src) => (
                <li
                  key={src.chunk_id || `${src.document}-${src.section}`}
                  className="flex gap-2 rounded-xl px-3 py-2.5 text-[11px] text-[rgba(228,232,242,0.45)]"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.06)',
                  }}
                >
                  <FileText size={13} className="mt-0.5 shrink-0 text-cyan-400" />
                  <span>
                    {src.document || src.source}
                    {src.section ? ` — ${src.section}` : ''}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div
          className="flex gap-3 rounded-xl p-4"
          style={{
            background: 'rgba(251,191,36,0.05)',
            border: '1px solid rgba(251,191,36,0.15)',
          }}
        >
          <AlertTriangle size={13} className="mt-0.5 shrink-0 text-amber-400" />
          <p className="text-[11px] leading-relaxed text-amber-100/55">
            <span className="font-semibold text-amber-100/75">Educational use only.</span>{' '}
            These are ML-based risk estimates, not a medical diagnosis. Always consult a
            qualified healthcare professional.
          </p>
        </div>
      </div>
    </motion.div>
  )
}
