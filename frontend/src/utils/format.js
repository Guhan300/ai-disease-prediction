/**
 * Format an ISO timestamp for compact chat display.
 * @param {string} value
 * @returns {string}
 */
export function formatChatTime(value) {
  if (!value) return ''
  try {
    return new Intl.DateTimeFormat(undefined, {
      hour: 'numeric',
      minute: '2-digit',
    }).format(new Date(value))
  } catch {
    return ''
  }
}
