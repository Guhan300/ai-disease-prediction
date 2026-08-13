import { AlertTriangle } from 'lucide-react'

export function SafetyAlert({ safety }) {
  if (!safety?.red_flag_detected) return null

  return (
    <div
      className="mt-3 flex gap-3 rounded-xl p-4"
      style={{
        background: 'rgba(251,191,36,0.05)',
        border: '1px solid rgba(251,191,36,0.15)',
      }}
      role="alert"
    >
      <AlertTriangle size={13} className="mt-0.5 shrink-0 text-amber-400" />
      <div>
        <p className="text-[12px] font-semibold text-amber-200/80">Safety notice</p>
        <p className="mt-1 text-[11px] leading-relaxed text-amber-100/55">
          {safety.message ||
            'Your response may indicate a situation requiring prompt medical attention.'}
        </p>
      </div>
    </div>
  )
}
