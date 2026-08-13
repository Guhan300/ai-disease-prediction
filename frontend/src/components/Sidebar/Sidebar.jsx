import { Brain, Menu, Plus, Search, Settings, X } from 'lucide-react'
import clsx from 'clsx'

export function Sidebar({
  isOpen,
  onClose,
  backendStatus,
  modelLoaded,
  sessionId,
  onNewAssessment,
  busy,
}) {
  const statusLabel =
    backendStatus === 'ok'
      ? 'Backend online'
      : backendStatus === 'checking'
        ? 'Checking backend…'
        : 'Backend offline'

  const statusColor =
    backendStatus === 'ok'
      ? 'bg-[var(--color-ok)]'
      : backendStatus === 'checking'
        ? 'bg-[var(--color-warn)]'
        : 'bg-[var(--color-danger)]'

  return (
    <>
      <div
        className={clsx(
          'fixed inset-0 z-20 bg-black/65 transition-opacity duration-200 md:hidden',
          isOpen ? 'opacity-100' : 'pointer-events-none opacity-0',
        )}
        onClick={onClose}
        aria-hidden={!isOpen}
      />

      <aside
        className={clsx(
          'fixed inset-y-0 left-0 z-30 flex h-full w-[260px] shrink-0 flex-col transition-transform duration-300 ease-in-out md:static md:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
        )}
        style={{
          background: 'var(--color-panel)',
          borderRight: '1px solid rgba(255,255,255,0.05)',
        }}
      >
        <div
          className="flex h-14 shrink-0 items-center gap-2.5 px-4"
          style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}
        >
          <div
            className="flex h-7 w-7 items-center justify-center rounded-xl"
            style={{
              background: 'linear-gradient(135deg, #22d3ee, #00c89a)',
              boxShadow: '0 0 14px rgba(6,182,212,0.28)',
            }}
          >
            <Brain size={14} className="text-white" />
          </div>
          <span className="text-[15px] font-bold tracking-tight text-[rgba(228,232,242,0.92)]">
            MedAI
          </span>
          <span
            className="ml-0.5 rounded px-1.5 py-0.5 font-mono text-[10px]"
            style={{
              background: 'rgba(6,182,212,0.10)',
              color: 'rgba(6,182,212,0.7)',
              border: '1px solid rgba(6,182,212,0.15)',
            }}
          >
            Beta
          </span>
          <button
            type="button"
            onClick={onClose}
            className="ml-auto rounded-lg p-1 text-[rgba(228,232,242,0.35)] transition hover:text-[rgba(228,232,242,0.7)] md:hidden"
            aria-label="Close sidebar"
          >
            <X size={15} />
          </button>
        </div>

        <div className="shrink-0 px-3 pb-2 pt-4">
          <button
            type="button"
            onClick={() => {
              onNewAssessment()
              onClose?.()
            }}
            disabled={busy}
            className="flex w-full items-center gap-2 rounded-xl px-3 py-2.5 text-sm font-semibold transition disabled:opacity-60"
            style={{
              background: 'rgba(6,182,212,0.09)',
              border: '1px solid rgba(6,182,212,0.20)',
              color: '#22d3ee',
            }}
          >
            <Plus size={15} />
            New Assessment
          </button>
        </div>

        <div className="shrink-0 px-3 pb-3">
          <div
            className="flex items-center gap-2 rounded-xl px-3 py-2.5"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <Search size={13} className="shrink-0 text-white/25" />
            <input
              type="text"
              placeholder="Search assessments..."
              disabled
              className="flex-1 bg-transparent text-[13px] text-[rgba(228,232,242,0.55)] outline-none placeholder:text-white/25"
            />
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-3">
          <div className="mb-2 px-2 font-mono text-[10px] uppercase tracking-[0.1em] text-white/25">
            Current session
          </div>
          <div
            className="mb-4 rounded-xl px-3 py-2.5"
            style={{
              background: 'rgba(255,255,255,0.04)',
              border: '1px solid rgba(255,255,255,0.06)',
            }}
          >
            <p className="truncate font-mono text-xs text-[rgba(228,232,242,0.55)]">
              {sessionId || 'No active session'}
            </p>
          </div>

          <div className="mb-2 px-2 font-mono text-[10px] uppercase tracking-[0.1em] text-white/25">
            Recent
          </div>
          <p className="px-2 text-[12px] leading-relaxed text-white/30">
            Session history will appear here when persisted assessments are available.
            No demo assessments are shown.
          </p>
        </div>

        <div
          className="shrink-0 space-y-2 p-3"
          style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}
        >
          <div
            className="rounded-xl px-3 py-2.5"
            style={{ background: 'rgba(255,255,255,0.03)' }}
          >
            <div className="flex items-center gap-2">
              <span className={clsx('h-2 w-2 rounded-full', statusColor)} />
              <p className="text-[13px] text-[rgba(228,232,242,0.65)]">{statusLabel}</p>
            </div>
            <p className="mt-1.5 text-[11px] text-white/30">
              {modelLoaded ? 'ML model loaded' : 'Model not loaded — train first'}
            </p>
          </div>
          <button
            type="button"
            className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-[13px] text-[rgba(228,232,242,0.35)] transition hover:bg-white/[0.04] hover:text-[rgba(228,232,242,0.65)]"
          >
            <Settings size={14} />
            Settings
          </button>
        </div>
      </aside>
    </>
  )
}

export function SidebarMenuButton({ onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-lg p-1.5 text-white/30 transition hover:bg-white/5 hover:text-white/60 md:hidden"
      aria-label="Open sidebar"
    >
      <Menu size={17} />
    </button>
  )
}
