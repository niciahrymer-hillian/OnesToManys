document.addEventListener("DOMContentLoaded", async () => {
  window.initPancakeMenu("home");

  const healthNode = document.getElementById("healthStatus");
  const countNode = document.getElementById("dataCounts");
  const manufacturerTable = document.getElementById("homeManufacturerTable");
  const productTable = document.getElementById("homeProductTable");

  function renderManufacturers(manufacturers) {
    if (!manufacturers.length) {
      manufacturerTable.innerHTML = '<p class="notice">No manufacturers available.</p>';
      return;
    }

    manufacturerTable.innerHTML = manufacturers
      .map(
        (item) => `
        <button type="button" class="item-button landing-button" data-manufacturer-id="${item.manufacturer_id}">
          <strong>#${item.manufacturer_id} ${item.name}</strong>
          <span>${item.country} · Founded ${item.founded_year}</span>
          <span class="landing-subtle">Open manufacturer details or browse its product set</span>
        </button>`
      )
      .join("");

    manufacturerTable.querySelectorAll("button[data-manufacturer-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const manufacturerId = button.dataset.manufacturerId;
        window.location.href = `manufacturers.html?manufacturer_id=${manufacturerId}`;
      });
    });
  }

  function renderProducts(products) {
    if (!products.length) {
      productTable.innerHTML = '<p class="notice">No products available.</p>';
      return;
    }

    const preview = products.slice(0, 40);
    productTable.innerHTML = preview
      .map(
        (item) => `
        <button type="button" class="item-button landing-button" data-product-id="${item.product_id}" data-manufacturer-id="${item.manufacturer_id}">
          <strong>#${item.product_id} ${item.product_name}</strong>
          <span>${item.category} · $${Number(item.price).toFixed(2)} · Stock ${item.stock_quantity}</span>
          <span class="landing-subtle">Open the product page for this manufacturer context</span>
        </button>`
      )
      .join("");

    productTable.querySelectorAll("button[data-product-id]").forEach((button) => {
      button.addEventListener("click", () => {
        const productId = button.dataset.productId;
        const manufacturerId = button.dataset.manufacturerId;
        window.location.href = `products.html?manufacturer_id=${manufacturerId}&product_id=${productId}`;
      });
    });
  }

  try {
    const [health, manufacturers, products] = await Promise.all([
      window.AppApi.getHealth(),
      window.AppApi.getManufacturers(),
      window.AppApi.getProducts(),
    ]);

    healthNode.textContent = health.message;
    countNode.textContent = `Manufacturers: ${manufacturers.length} | Products: ${products.length}`;
    renderManufacturers(manufacturers);
    renderProducts(products);
  } catch (error) {
    healthNode.textContent = "Unable to reach backend API";
    healthNode.classList.add("error");
    countNode.textContent = error.message;
    manufacturerTable.innerHTML = '<p class="error">Could not load manufacturer directory.</p>';
    productTable.innerHTML = '<p class="error">Could not load product directory.</p>';
  }
});
