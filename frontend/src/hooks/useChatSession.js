import { useCallback, useEffect, useState } from 'react'
import {
  createChatSession,
  fetchHealth,
  sendChatMessage,
} from '../services/api'

export function useChatSession() {
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [backendStatus, setBackendStatus] = useState('checking')
  const [isTyping, setIsTyping] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(null)
  const [modelLoaded, setModelLoaded] = useState(false)

  const checkHealth = useCallback(async () => {
    setBackendStatus('checking')
    try {
      const health = await fetchHealth()
      setBackendStatus(health.status === 'ok' ? 'ok' : 'error')
      setModelLoaded(health.components?.model === 'ok')
      return health
    } catch {
      setBackendStatus('error')
      setModelLoaded(false)
      return null
    }
  }, [])

  const startSession = useCallback(async () => {
    setBusy(true)
    setError(null)
    setIsTyping(true)
    try {
      await checkHealth()
      const session = await createChatSession()
      setSessionId(session.session_id)
      setMessages([session.message])
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Could not create a chat session. Is the backend running?',
      )
      setMessages([])
      setSessionId(null)
    } finally {
      setIsTyping(false)
      setBusy(false)
    }
  }, [checkHealth])

  const sendMessage = useCallback(
    async (text) => {
      if (!sessionId || !text.trim()) return

      const optimisticUser = {
        id: `local-${Date.now()}`,
        role: 'user',
        content: text.trim(),
        created_at: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, optimisticUser])
      setBusy(true)
      setIsTyping(true)
      setError(null)

      try {
        const response = await sendChatMessage(sessionId, text.trim())
        const assistantMessage = {
          ...response.message,
          prediction: response.prediction,
          explanation: response.explanation,
          safety: response.safety,
          sources: response.sources,
          type: response.type,
        }
        setMessages((prev) => [...prev, assistantMessage])
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to send message. Please try again.',
        )
      } finally {
        setIsTyping(false)
        setBusy(false)
      }
    },
    [sessionId],
  )

  useEffect(() => {
    startSession()
  }, [startSession])

  return {
    sessionId,
    messages,
    backendStatus,
    modelLoaded,
    isTyping,
    busy,
    error,
    startSession,
    sendMessage,
  }
}
