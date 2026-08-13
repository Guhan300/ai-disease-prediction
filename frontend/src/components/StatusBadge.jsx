export function StatusBadge({ status }) {
  const normalized = (status || 'unknown').toLowerCase()
  const styles =
    normalized === 'ok'
      ? 'bg-emerald-400/10 text-emerald-300 ring-emerald-400/30'
      : normalized === 'not_loaded' || normalized === 'not_checked'
        ? 'bg-amber-400/10 text-amber-200 ring-amber-400/30'
        : 'bg-rose-400/10 text-rose-300 ring-rose-400/30'

  const label = normalized.replaceAll('_', ' ')

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ring-1 ring-inset ${styles}`}
    >
      {label}
    </span>
  )
}
