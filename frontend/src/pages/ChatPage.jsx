import { useState } from 'react'
import { ChatInput, ChatWindow } from '../components/Chat'
import { Sidebar, SidebarMenuButton } from '../components/Sidebar'
import { useChatSession } from '../hooks/useChatSession'

export function ChatPage() {
  const {
    sessionId,
    messages,
    backendStatus,
    modelLoaded,
    isTyping,
    busy,
    error,
    startSession,
    sendMessage,
  } = useChatSession()
  const [draft, setDraft] = useState('')
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Show Figma-style empty state until the user sends a real message.
  // Welcome from the API remains in session history and appears once chat starts.
  const userHasSpoken = messages.some((m) => m.role === 'user')
  const showEmptyState = !userHasSpoken

  async function handleSend() {
    const text = draft.trim()
    if (!text || busy) return
    setDraft('')
    await sendMessage(text)
  }

  async function handleSuggestion(text) {
    if (!text || busy || !sessionId) return
    setDraft('')
    await sendMessage(text)
  }

  return (
    <div
      className="flex h-screen w-screen overflow-hidden"
      style={{ background: '#080c14', color: '#e4e8f2' }}
    >
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        backendStatus={backendStatus}
        modelLoaded={modelLoaded}
        sessionId={sessionId}
        onNewAssessment={startSession}
        busy={busy}
      />

      <section className="flex min-w-0 flex-1 flex-col">
        <header
          className="flex h-14 shrink-0 items-center gap-3 px-5"
          style={{
            borderBottom: '1px solid rgba(255,255,255,0.05)',
            background: 'rgba(8,12,20,0.92)',
            backdropFilter: 'blur(12px)',
          }}
        >
          <SidebarMenuButton onClick={() => setSidebarOpen(true)} />

          <div className="flex items-center gap-2.5">
            <span className="status-dot-live h-2 w-2 rounded-full bg-teal-400" />
            <span className="text-[14px] font-semibold text-[rgba(228,232,242,0.82)]">
              MedAI
            </span>
            <span className="text-white/20">·</span>
            <span className="text-[13px] text-[rgba(228,232,242,0.38)]">
              AI Health Assistant
            </span>
          </div>

          <div className="ml-auto hidden font-mono text-[11px] text-white/20 sm:block">
            {modelLoaded ? 'Model ready' : 'Model offline'}
          </div>
        </header>

        <ChatWindow
          messages={messages}
          isTyping={isTyping}
          error={error}
          showEmptyState={showEmptyState}
          onSuggestion={handleSuggestion}
        />

        <ChatInput
          value={draft}
          onChange={setDraft}
          onSend={handleSend}
          disabled={busy || !sessionId}
        />
      </section>
    </div>
  )
}
