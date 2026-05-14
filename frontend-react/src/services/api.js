const API_PROTOCOL = import.meta.env.VITE_API_PROTOCOL || (window.location.protocol === 'https:' ? 'https' : 'http')
const API_HOST = import.meta.env.VITE_API_HOST || '127.0.0.1'
const API_PORT = import.meta.env.VITE_API_PORT || '5000'
const API_BASE = import.meta.env.VITE_API_BASE || `${API_PROTOCOL}://${API_HOST}:${API_PORT}/api`

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = payload.error || `Request failed (${response.status})`
    throw new Error(message)
  }
  return payload
}

async function requestJson(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options)
  return parseResponse(response)
}


/**
 * Fetch all manufacturers.
 * @returns {Promise<Array>} List of manufacturers
 */
export async function getManufacturers() {
  return requestJson('/manufacturers')
}


/**
 * Fetch a single manufacturer by ID.
 * @param {number} manufacturerId
 * @returns {Promise<Object>} Manufacturer object
 */
export async function getManufacturer(manufacturerId) {
  return requestJson(`/manufacturers/${manufacturerId}`)
}


/**
 * Fetch all products for a manufacturer.
 * @param {number} manufacturerId
 * @returns {Promise<Array>} List of products
 */
export async function getManufacturerProducts(manufacturerId) {
  return requestJson(`/manufacturers/${manufacturerId}/products`)
}


/**
 * Fetch all products.
 * @returns {Promise<Array>} List of all products
 */
export async function getProducts() {
  return requestJson('/products')
}


/**
 * Create a new manufacturer.
 * @param {Object} payload
 * @returns {Promise<Object>} Created manufacturer
 */
export async function createManufacturer(payload) {
  return requestJson('/manufacturers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


/**
 * Update a manufacturer by ID.
 * @param {number} manufacturerId
 * @param {Object} payload
 * @returns {Promise<Object>} Updated manufacturer
 */
export async function updateManufacturer(manufacturerId, payload) {
  return requestJson(`/manufacturers/${manufacturerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


/**
 * Delete a manufacturer by ID.
 * @param {number} manufacturerId
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteManufacturer(manufacturerId) {
  return requestJson(`/manufacturers/${manufacturerId}`, {
    method: 'DELETE',
  })
}


/**
 * Create a new product for a manufacturer.
 * @param {number} manufacturerId
 * @param {Object} payload
 * @returns {Promise<Object>} Created product
 */
export async function createManufacturerProduct(manufacturerId, payload) {
  return requestJson(`/manufacturers/${manufacturerId}/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


/**
 * Update a product for a manufacturer.
 * @param {number} manufacturerId
 * @param {number} productId
 * @param {Object} payload
 * @returns {Promise<Object>} Updated product
 */
export async function updateManufacturerProduct(manufacturerId, productId, payload) {
  return requestJson(`/manufacturers/${manufacturerId}/products/${productId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}


/**
 * Delete a product for a manufacturer.
 * @param {number} manufacturerId
 * @param {number} productId
 * @returns {Promise<Object>} Deletion result
 */
export async function deleteManufacturerProduct(manufacturerId, productId) {
  return requestJson(`/manufacturers/${manufacturerId}/products/${productId}`, {
    method: 'DELETE',
  })
}
