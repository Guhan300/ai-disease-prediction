const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || ''

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const payload = await response.json()
      detail = payload.detail || detail
    } catch {
      // keep default detail
    }
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }

  return response.json()
}

export function fetchHealth() {
  return request('/api/health')
}

export function createChatSession() {
  return request('/api/chat/session', { method: 'POST' })
}

export function getChatSession(sessionId) {
  return request(`/api/chat/session/${sessionId}`)
}

export function sendChatMessage(sessionId, message) {
  return request('/api/chat/message', {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId, message }),
  })
}
