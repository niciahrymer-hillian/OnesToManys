// [FILE] api_annotated_cp.js
// [WHY] Centralizes frontend HTTP calls to backend REST API.
// [EFFECT] Components stay focused on UI/state while this layer handles requests/errors.

// [CONSTANT] Shared API base URL for local Flask backend.
const API_BASE = 'http://127.0.0.1:5000/api'

// [FUNCTION] Normalize successful/error JSON responses.
async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = payload.error || `Request failed (${response.status})`
    throw new Error(message)
  }
  return payload
}

// [FUNCTION] Fetch all manufacturers.
export async function getManufacturers() {
  const response = await fetch(`${API_BASE}/manufacturers`)
  return parseResponse(response)
}

// [FUNCTION] Fetch one manufacturer by id.
export async function getManufacturer(manufacturerId) {
  const response = await fetch(`${API_BASE}/manufacturers/${manufacturerId}`)
  return parseResponse(response)
}

// [FUNCTION] Fetch products scoped to one manufacturer.
export async function getManufacturerProducts(manufacturerId) {
  const response = await fetch(`${API_BASE}/manufacturers/${manufacturerId}/products`)
  return parseResponse(response)
}
