const API_BASE = 'http://127.0.0.1:5000/api'

async function parseResponse(response) {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = payload.error || `Request failed (${response.status})`
    throw new Error(message)
  }
  return payload
}

export async function getManufacturers() {
  const response = await fetch(`${API_BASE}/manufacturers`)
  return parseResponse(response)
}

export async function getManufacturer(manufacturerId) {
  const response = await fetch(`${API_BASE}/manufacturers/${manufacturerId}`)
  return parseResponse(response)
}

export async function getManufacturerProducts(manufacturerId) {
  const response = await fetch(`${API_BASE}/manufacturers/${manufacturerId}/products`)
  return parseResponse(response)
}
