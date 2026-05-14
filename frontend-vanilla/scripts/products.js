document.addEventListener("DOMContentLoaded", async () => {
  window.initPancakeMenu("products");

  const manufacturerSelect = document.getElementById("manufacturerSelect");
  const productSearch = document.getElementById("productSearch");
  const productForm = document.getElementById("productForm");
  const productSubmitBtn = document.getElementById("productSubmitBtn");
  const cancelEditBtn = document.getElementById("cancelEditBtn");
  const productError = document.getElementById("productError");
  const productTable = document.getElementById("productTable");
  const query = new URLSearchParams(window.location.search);
  const preselectManufacturerId = Number(query.get("manufacturer_id"));
  const preselectProductId = Number(query.get("product_id"));
  const preselectCategory = query.get("category") || "";

  let manufacturers = [];
  let products = [];
  let editingProductId = null;

  if (preselectCategory) {
    productSearch.value = preselectCategory;
  }

  function updateUrlState() {
    const manufacturerId = selectedManufacturerId();
    if (!manufacturerId) {
      return;
    }
    const url = new URL(window.location.href);
    url.searchParams.set("manufacturer_id", String(manufacturerId));
    window.history.replaceState({}, "", url.toString());
  }

  function selectedManufacturerId() {
    return Number(manufacturerSelect.value);
  }

  function resetProductForm() {
    productForm.reset();
    editingProductId = null;
    productSubmitBtn.textContent = "Add Product";
    cancelEditBtn.disabled = true;
  }

  function setEditProduct(item) {
    editingProductId = item.product_id;
    productSubmitBtn.textContent = "Update Product";
    cancelEditBtn.disabled = false;

    productForm.product_name.value = item.product_name;
    productForm.category.value = item.category;
    productForm.price.value = item.price;
    productForm.stock_quantity.value = item.stock_quantity;
    productForm.description.value = item.description || "";

    const url = new URL(window.location.href);
    url.searchParams.set("product_id", String(item.product_id));
    window.history.replaceState({}, "", url.toString());
  }

  function renderProducts() {
    const term = productSearch.value.trim().toLowerCase();
    const filtered = products.filter((item) => {
      if (!term) {
        return true;
      }
      return [item.product_name, item.category, item.description || ""].join(" ").toLowerCase().includes(term);
    });

    if (filtered.length === 0) {
      productTable.innerHTML = '<p class="notice">No products found for this manufacturer.</p>';
      return;
    }

    const header = '<div class="row header"><span>Product</span><span>Category</span><span>Price</span><span>Stock</span><span>Actions</span></div>';
    const rows = filtered
      .map(
        (item) => `
        <div class="row">
          <span><a class="attr-link" href="products.html?manufacturer_id=${item.manufacturer_id}&product_id=${item.product_id}">#${item.product_id} ${item.product_name}</a></span>
          <span><a class="muted-link" href="products.html?manufacturer_id=${item.manufacturer_id}&category=${encodeURIComponent(item.category)}">${item.category}</a></span>
          <span>$${Number(item.price).toFixed(2)}</span>
          <span>${item.stock_quantity}</span>
          <span class="actions">
            <a class="quick-link" href="manufacturers.html?manufacturer_id=${item.manufacturer_id}">Manufacturer ${item.manufacturer_id}</a>
            <button type="button" class="ghost" data-edit="${item.product_id}">Edit</button>
            <button type="button" class="danger" data-delete="${item.product_id}">Delete</button>
          </span>
        </div>`
      )
      .join("");

    productTable.innerHTML = header + rows;

    productTable.querySelectorAll("button[data-edit]").forEach((button) => {
      button.addEventListener("click", () => {
        const id = Number(button.dataset.edit);
        const item = products.find((p) => p.product_id === id);
        if (!item) {
          return;
        }
        setEditProduct(item);
      });
    });

    productTable.querySelectorAll("button[data-delete]").forEach((button) => {
      button.addEventListener("click", async () => {
        const id = Number(button.dataset.delete);
        if (!window.confirm("Delete this product?")) {
          return;
        }

        try {
          productError.textContent = "";
          await window.AppApi.deleteManufacturerProduct(selectedManufacturerId(), id);
          await loadProducts();
          if (editingProductId === id) {
            resetProductForm();
          }
        } catch (error) {
          productError.textContent = error.message;
        }
      });
    });
  }

  async function loadManufacturers() {
    manufacturers = await window.AppApi.getManufacturers();
    manufacturerSelect.innerHTML = "";

    if (manufacturers.length === 0) {
      manufacturerSelect.innerHTML = '<option value="">No manufacturers found</option>';
      products = [];
      renderProducts();
      return;
    }

    manufacturers.forEach((item) => {
      const option = document.createElement("option");
      option.value = String(item.manufacturer_id);
      option.textContent = `${item.name} (${item.country})`;
      manufacturerSelect.appendChild(option);
    });

    const saved = Number(localStorage.getItem("selectedManufacturerId"));
    let useId = manufacturers[0].manufacturer_id;
    if (preselectManufacturerId && manufacturers.some((m) => m.manufacturer_id === preselectManufacturerId)) {
      useId = preselectManufacturerId;
    } else if (manufacturers.some((m) => m.manufacturer_id === saved)) {
      useId = saved;
    }
    manufacturerSelect.value = String(useId);
    updateUrlState();
  }

  async function loadProducts() {
    const manufacturerId = selectedManufacturerId();
    if (!manufacturerId) {
      products = [];
      renderProducts();
      return;
    }

    localStorage.setItem("selectedManufacturerId", String(manufacturerId));
    products = await window.AppApi.getManufacturerProducts(manufacturerId);
    renderProducts();

    if (preselectProductId) {
      const selected = products.find((item) => item.product_id === preselectProductId);
      if (selected) {
        setEditProduct(selected);
      }
    }
  }

  manufacturerSelect.addEventListener("change", async () => {
    resetProductForm();
    updateUrlState();
    await loadProducts();
  });

  productSearch.addEventListener("input", renderProducts);

  productForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const manufacturerId = selectedManufacturerId();
    if (!manufacturerId) {
      return;
    }

    productError.textContent = "";

    try {
      const payload = {
        product_name: productForm.product_name.value.trim(),
        category: productForm.category.value.trim(),
        price: Number(productForm.price.value),
        stock_quantity: Number(productForm.stock_quantity.value),
        description: productForm.description.value.trim() || null,
      };

      if (editingProductId) {
        await window.AppApi.updateManufacturerProduct(manufacturerId, editingProductId, payload);
      } else {
        await window.AppApi.createManufacturerProduct(manufacturerId, payload);
      }

      resetProductForm();
      await loadProducts();
    } catch (error) {
      productError.textContent = error.message;
    }
  });

  cancelEditBtn.addEventListener("click", () => {
    resetProductForm();
    const url = new URL(window.location.href);
    url.searchParams.delete("product_id");
    window.history.replaceState({}, "", url.toString());
  });

  try {
    await loadManufacturers();
    await loadProducts();
  } catch (error) {
    productError.textContent = error.message;
  }
});
