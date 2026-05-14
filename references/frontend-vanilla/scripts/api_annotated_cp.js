// [FILE] api_annotated_cp.js
// [WHY] Single place for Vanilla frontend API calls.
// [EFFECT] Pages can focus on UI logic and share the same error behavior.

(function () {
  const API_BASE = "http://127.0.0.1:5000/api";

  // [FUNCTION] Normalize API errors and parsed JSON payloads.
  async function parseResponse(response) {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || `Request failed (${response.status})`);
    }
    return payload;
  }

  // [FUNCTION] Wrapper for API requests.
  async function request(path, options) {
    const response = await fetch(`${API_BASE}${path}`, options);
    return parseResponse(response);
  }

  // [EXPORT] Public API surface used by all Vanilla pages.
  window.AppApi = {
    getHealth: () => fetch("http://127.0.0.1:5000/").then(parseResponse),
    getManufacturers: () => request("/manufacturers"),
    getManufacturer: (id) => request(`/manufacturers/${id}`),
    createManufacturer: (payload) =>
      request("/manufacturers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    updateManufacturer: (id, payload) =>
      request(`/manufacturers/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    deleteManufacturer: (id) => request(`/manufacturers/${id}`, { method: "DELETE" }),
    getManufacturerProducts: (id) => request(`/manufacturers/${id}/products`),
    createManufacturerProduct: (id, payload) =>
      request(`/manufacturers/${id}/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    updateManufacturerProduct: (manufacturerId, productId, payload) =>
      request(`/manufacturers/${manufacturerId}/products/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    deleteManufacturerProduct: (manufacturerId, productId) =>
      request(`/manufacturers/${manufacturerId}/products/${productId}`, { method: "DELETE" }),
    getProducts: () => request("/products"),
  };
})();
