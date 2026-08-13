import { useEffect, useRef } from 'react'
import { Send } from 'lucide-react'

export function ChatInput({ value, onChange, onSend, disabled }) {
  const textareaRef = useRef(null)

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 128)}px`
  }, [value])

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      if (!disabled && value.trim()) onSend()
    }
  }

  const canSend = Boolean(value.trim()) && !disabled

  return (
    <div
      className="shrink-0 px-4 py-4 sm:px-6"
      style={{
        borderTop: '1px solid rgba(255,255,255,0.05)',
        background: 'rgba(8,12,20,0.92)',
        backdropFilter: 'blur(12px)',
      }}
    >
      <div className="mx-auto max-w-[680px]">
        <div
          className="flex items-end gap-3 rounded-2xl px-4 py-3"
          style={{
            background: '#0d1524',
            border: '1px solid rgba(255,255,255,0.08)',
          }}
        >
          <label className="sr-only" htmlFor="medai-chat-input">
            Message MedAI
          </label>
          <textarea
            id="medai-chat-input"
            ref={textareaRef}
            rows={1}
            value={value}
            disabled={disabled}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tell me what you're experiencing..."
            className="max-h-32 min-h-[22px] flex-1 resize-none bg-transparent text-[14px] leading-relaxed text-[rgba(228,232,242,0.8)] outline-none disabled:opacity-60"
          />
          <button
            type="button"
            onClick={onSend}
            disabled={!canSend}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl transition"
            style={
              canSend
                ? {
                    background: '#00c89a',
                    color: '#080c14',
                    boxShadow: '0 0 18px rgba(0,200,154,0.22)',
                  }
                : {
                    background: 'rgba(255,255,255,0.05)',
                    color: 'rgba(255,255,255,0.2)',
                    cursor: 'not-allowed',
                  }
            }
            aria-label="Send message"
          >
            <Send size={13} />
          </button>
        </div>
        <p className="mt-2 text-center font-mono text-[10px] text-white/20">
          For educational purposes only — not a substitute for professional medical advice
        </p>
      </div>
    </div>
  )
}
