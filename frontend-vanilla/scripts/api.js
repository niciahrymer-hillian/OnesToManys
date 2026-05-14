(function () {
  const API_BASE = "http://127.0.0.1:5000/api";

  async function parseResponse(response) {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.error || `Request failed (${response.status})`);
    }
    return payload;
  }

  async function request(path, options) {
    const response = await fetch(`${API_BASE}${path}`, options);
    return parseResponse(response);
  }

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
