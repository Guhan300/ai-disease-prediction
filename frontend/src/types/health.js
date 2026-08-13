/**
 * @typedef {Object} HealthComponents
 * @property {string} [api]
 * @property {string} [model]
 * @property {string} [rag]
 * @property {string} [llm]
 */

/**
 * @typedef {Object} HealthResponse
 * @property {string} status
 * @property {string} app_name
 * @property {string} version
 * @property {string} environment
 * @property {string} timestamp
 * @property {HealthComponents} components
 * @property {string|null} [message]
 */

export {}
