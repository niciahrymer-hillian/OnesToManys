// [FILE] api_annotated_cp.js
// [WHY] Frontend API client with protocol-aware base URL so React can call HTTP or HTTPS backend automatically.
// [EFFECT] Uses HTTPS when frontend is served over HTTPS or env vars explicitly request it.

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

export async function getManufacturers() {
  return requestJson('/manufacturers')
}

export async function getManufacturer(manufacturerId) {
  return requestJson(`/manufacturers/${manufacturerId}`)
}

export async function getManufacturerProducts(manufacturerId) {
  return requestJson(`/manufacturers/${manufacturerId}/products`)
}

export async function getProducts() {
  return requestJson('/products')
}

export async function createManufacturer(payload) {
  return requestJson('/manufacturers', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function updateManufacturer(manufacturerId, payload) {
  return requestJson(`/manufacturers/${manufacturerId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function deleteManufacturer(manufacturerId) {
  return requestJson(`/manufacturers/${manufacturerId}`, {
    method: 'DELETE',
  })
}

export async function createManufacturerProduct(manufacturerId, payload) {
  return requestJson(`/manufacturers/${manufacturerId}/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function updateManufacturerProduct(manufacturerId, productId, payload) {
  return requestJson(`/manufacturers/${manufacturerId}/products/${productId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function deleteManufacturerProduct(manufacturerId, productId) {
  return requestJson(`/manufacturers/${manufacturerId}/products/${productId}`, {
    method: 'DELETE',
  })
}
