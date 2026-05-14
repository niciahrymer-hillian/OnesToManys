// [FILE] manufacturers_annotated_cp.js
// [WHY] Implements Vanilla manufacturer CRUD and search interactions.
// [EFFECT] Provides a complete master-entity management page.

document.addEventListener("DOMContentLoaded", async () => {
  window.initPancakeMenu("manufacturers");

  // [ELEMENTS] All interactive controls on the page.
  const createForm = document.getElementById("createManufacturerForm");
  const editForm = document.getElementById("editManufacturerForm");
  const deleteBtn = document.getElementById("deleteManufacturerBtn");
  const listNode = document.getElementById("manufacturerList");
  const searchInput = document.getElementById("manufacturerSearch");
  const createError = document.getElementById("createError");
  const editError = document.getElementById("editError");
  const selectedHint = document.getElementById("selectedHint");
  const manufacturerProductTable = document.getElementById("manufacturerProductTable");
  const query = new URLSearchParams(window.location.search);
  const preselectId = Number(query.get("manufacturer_id"));
  const countryFilter = query.get("country") || "";
  const foundedFilter = query.get("founded_year") || "";

  let manufacturers = [];
  let selectedProducts = [];
  let selectedId = null;

  if (countryFilter) {
    searchInput.value = countryFilter;
  }
  if (foundedFilter) {
    searchInput.value = foundedFilter;
  }

  function updateUrlState() {
    if (!selectedId) {
      return;
    }
    const url = new URL(window.location.href);
    url.searchParams.set("manufacturer_id", String(selectedId));
    window.history.replaceState({}, "", url.toString());
  }

  async function loadSelectedProducts() {
    if (!selectedId) {
      selectedProducts = [];
      return;
    }
    selectedProducts = await window.AppApi.getManufacturerProducts(selectedId);
  }

  function renderSelectedProductsTable() {
    if (!selectedId) {
      manufacturerProductTable.innerHTML = '<p class="notice">Select a manufacturer to view related products.</p>';
      return;
    }

    if (!selectedProducts.length) {
      manufacturerProductTable.innerHTML = '<p class="notice">No products found for this manufacturer.</p>';
      return;
    }

    const header = '<div class="row header"><span>Product</span><span>Category</span><span>Price</span><span>Stock</span><span>Open</span></div>';
    const rows = selectedProducts
      .map(
        (item) => `
        <div class="row">
          <span><a class="attr-link" href="products.html?manufacturer_id=${selectedId}&product_id=${item.product_id}">#${item.product_id} ${item.product_name}</a></span>
          <span><a class="muted-link" href="products.html?manufacturer_id=${selectedId}&category=${encodeURIComponent(item.category)}">${item.category}</a></span>
          <span>$${Number(item.price).toFixed(2)}</span>
          <span>${item.stock_quantity}</span>
          <span class="actions"><a class="quick-link" href="products.html?manufacturer_id=${selectedId}&product_id=${item.product_id}">Edit Product</a></span>
        </div>`
      )
      .join("");

    manufacturerProductTable.innerHTML = header + rows;
  }

  async function setSelected(id) {
    selectedId = id;
    localStorage.setItem("selectedManufacturerId", String(id));
    const selected = manufacturers.find((item) => item.manufacturer_id === id);
    if (!selected) {
      selectedHint.textContent = "Select a manufacturer from the list.";
      editForm.reset();
      selectedProducts = [];
      renderSelectedProductsTable();
      return;
    }

    selectedHint.textContent = `Editing #${id}: ${selected.name}`;
    editForm.name.value = selected.name;
    editForm.country.value = selected.country;
    editForm.founded_year.value = selected.founded_year;
    editForm.headquarters_city.value = selected.headquarters_city;
    editForm.is_active.value = String(Boolean(selected.is_active));
    updateUrlState();
    await loadSelectedProducts();
    renderSelectedProductsTable();
  }

  function renderList() {
    const term = searchInput.value.trim().toLowerCase();
    const filtered = manufacturers.filter((item) => {
      if (!term) {
        return true;
      }
      return [item.name, item.country, item.headquarters_city].join(" ").toLowerCase().includes(term);
    });

    listNode.innerHTML = "";
    if (filtered.length === 0) {
      listNode.innerHTML = '<p class="notice">No manufacturers found.</p>';
      return;
    }

    filtered.forEach((item) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = `item-button${item.manufacturer_id === selectedId ? " is-active" : ""}`;
      button.innerHTML = `<strong><a class="attr-link" href="products.html?manufacturer_id=${item.manufacturer_id}">#${item.manufacturer_id} ${item.name}</a></strong><br /><span><a class="muted-link" href="manufacturers.html?country=${encodeURIComponent(item.country)}">${item.country}</a> · Founded <a class="muted-link" href="manufacturers.html?founded_year=${item.founded_year}">${item.founded_year}</a></span>`;
      button.addEventListener("click", async () => {
        await setSelected(item.manufacturer_id);
        renderList();
      });
      listNode.appendChild(button);
    });
  }

  async function loadManufacturers() {
    manufacturers = await window.AppApi.getManufacturers();
    if (!selectedId && manufacturers.length > 0) {
      const saved = Number(localStorage.getItem("selectedManufacturerId"));
      if (preselectId && manufacturers.some((m) => m.manufacturer_id === preselectId)) {
        selectedId = preselectId;
      } else {
        selectedId = manufacturers.some((m) => m.manufacturer_id === saved)
          ? saved
          : manufacturers[0].manufacturer_id;
      }
    }
    if (selectedId && !manufacturers.some((m) => m.manufacturer_id === selectedId)) {
      selectedId = manufacturers[0]?.manufacturer_id || null;
    }
    renderList();
    if (selectedId) {
      await setSelected(selectedId);
    }
  }

  createForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    createError.textContent = "";

    try {
      const payload = {
        name: createForm.name.value.trim(),
        country: createForm.country.value.trim(),
        founded_year: Number(createForm.founded_year.value),
        headquarters_city: createForm.headquarters_city.value.trim(),
      };
      const created = await window.AppApi.createManufacturer(payload);
      createForm.reset();
      await loadManufacturers();
      await setSelected(created.manufacturer_id);
      renderList();
    } catch (error) {
      createError.textContent = error.message;
    }
  });

  editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    editError.textContent = "";
    if (!selectedId) {
      return;
    }

    try {
      const payload = {
        name: editForm.name.value.trim(),
        country: editForm.country.value.trim(),
        founded_year: Number(editForm.founded_year.value),
        headquarters_city: editForm.headquarters_city.value.trim(),
        is_active: editForm.is_active.value === "true",
      };
      await window.AppApi.updateManufacturer(selectedId, payload);
      await loadManufacturers();
      await setSelected(selectedId);
      renderList();
    } catch (error) {
      editError.textContent = error.message;
    }
  });

  deleteBtn.addEventListener("click", async () => {
    editError.textContent = "";
    if (!selectedId) {
      return;
    }
    if (!window.confirm("Delete this manufacturer and all nested products?")) {
      return;
    }

    try {
      await window.AppApi.deleteManufacturer(selectedId);
      selectedId = null;
      await loadManufacturers();
    } catch (error) {
      editError.textContent = error.message;
    }
  });

  searchInput.addEventListener("input", renderList);

  try {
    await loadManufacturers();
  } catch (error) {
    createError.textContent = error.message;
    manufacturerProductTable.innerHTML = '<p class="error">Could not load manufacturer products.</p>';
  }
});
