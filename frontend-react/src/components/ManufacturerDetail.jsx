import { useEffect, useState } from 'react'
import ProductList from './ProductList'

const emptyProductForm = {
  product_name: '',
  category: '',
  price: '',
  stock_quantity: '',
  description: '',
}

function ManufacturerDetail({
  manufacturer,
  products,
  isLoadingProducts,
  detailsError,
  onUpdateManufacturer,
  onDeleteManufacturer,
  onCreateProduct,
  onUpdateProduct,
  onDeleteProduct,
  isSavingManufacturer,
  isSavingProduct,
  manufacturerActionError,
  productActionError,
}) {
  const [manufacturerForm, setManufacturerForm] = useState(null)
  const [productForm, setProductForm] = useState(emptyProductForm)
  const [editingProductId, setEditingProductId] = useState(null)
  const [deletingProductId, setDeletingProductId] = useState(null)
  const [productSearch, setProductSearch] = useState('')

  const totalUnitsSold = products.reduce((sum, product) => sum + Number(product.units_sold || 0), 0)
  const totalRevenue = products.reduce((sum, product) => sum + Number(product.revenue || 0), 0)

  const topOrigin = Object.entries(
    products.reduce((accumulator, product) => {
      const origin = product.order_origin || 'Unknown'
      accumulator[origin] = (accumulator[origin] || 0) + Number(product.units_sold || 0)
      return accumulator
    }, {}),
  ).sort((left, right) => right[1] - left[1])[0]?.[0]

  const topChannel = Object.entries(
    products.reduce((accumulator, product) => {
      const channel = product.sales_channel || 'Unknown'
      accumulator[channel] = (accumulator[channel] || 0) + Number(product.units_sold || 0)
      return accumulator
    }, {}),
  ).sort((left, right) => right[1] - left[1])[0]?.[0]

  const filteredProducts = products.filter((product) => {
    const term = productSearch.trim().toLowerCase()
    if (!term) {
      return true
    }
    return [product.product_name, product.category, product.description || '']
      .join(' ')
      .toLowerCase()
      .includes(term)
  })

  useEffect(() => {
    if (!manufacturer) {
      setManufacturerForm(null)
      return
    }
    setManufacturerForm({
      name: manufacturer.name,
      country: manufacturer.country,
      founded_year: String(manufacturer.founded_year),
      headquarters_city: manufacturer.headquarters_city,
      is_active: manufacturer.is_active,
    })
  }, [manufacturer])

  useEffect(() => {
    setProductForm(emptyProductForm)
    setEditingProductId(null)
    setDeletingProductId(null)
    setProductSearch('')
  }, [manufacturer?.manufacturer_id])

  if (!manufacturer) {
    return (
      <section className="detail-panel">
        <p className="status-text">Choose a manufacturer to view details and products.</p>
      </section>
    )
  }

  async function handleManufacturerSubmit(event) {
    event.preventDefault()
    await onUpdateManufacturer({
      ...manufacturerForm,
      founded_year: Number(manufacturerForm.founded_year),
    })
  }

  async function handleProductSubmit(event) {
    event.preventDefault()
    const payload = {
      ...productForm,
      price: Number(productForm.price),
      stock_quantity: Number(productForm.stock_quantity),
      description: productForm.description || null,
    }

    if (editingProductId) {
      await onUpdateProduct(editingProductId, payload)
    } else {
      await onCreateProduct(payload)
    }

    setProductForm(emptyProductForm)
    setEditingProductId(null)
  }

  function handleEditProduct(product) {
    setEditingProductId(product.product_id)
    setProductForm({
      product_name: product.product_name,
      category: product.category,
      price: String(product.price),
      stock_quantity: String(product.stock_quantity),
      description: product.description || '',
    })
  }

  async function handleDeleteProduct(productId) {
    setDeletingProductId(productId)
    await onDeleteProduct(productId)
    setDeletingProductId(null)

    if (editingProductId === productId) {
      setProductForm(emptyProductForm)
      setEditingProductId(null)
    }
  }

  return (
    <section className="detail-panel" aria-live="polite">
      <header className="detail-header">
        <h2>{manufacturer.name}</h2>
        <p>
          {manufacturer.headquarters_city}, {manufacturer.country}
        </p>
      </header>

      <dl className="detail-facts">
        <div>
          <dt>Founded</dt>
          <dd>{manufacturer.founded_year}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{manufacturer.is_active ? 'Active' : 'Inactive'}</dd>
        </div>
        <div>
          <dt>Units Sold</dt>
          <dd>{totalUnitsSold}</dd>
        </div>
        <div>
          <dt>Revenue</dt>
          <dd>${totalRevenue.toFixed(2)}</dd>
        </div>
        <div>
          <dt>Top Region</dt>
          <dd>{topOrigin || 'n/a'}</dd>
        </div>
        <div>
          <dt>Top Channel</dt>
          <dd>{topChannel || 'n/a'}</dd>
        </div>
      </dl>

      <div className="crud-section">
        <h3>Edit Manufacturer</h3>
        <form className="editor-form" onSubmit={handleManufacturerSubmit}>
          <label>
            Name
            <input
              value={manufacturerForm?.name || ''}
              onChange={(event) =>
                setManufacturerForm((prev) => ({ ...prev, name: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Country
            <input
              value={manufacturerForm?.country || ''}
              onChange={(event) =>
                setManufacturerForm((prev) => ({ ...prev, country: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Founded Year
            <input
              type="number"
              value={manufacturerForm?.founded_year || ''}
              onChange={(event) =>
                setManufacturerForm((prev) => ({ ...prev, founded_year: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Headquarters City
            <input
              value={manufacturerForm?.headquarters_city || ''}
              onChange={(event) =>
                setManufacturerForm((prev) => ({ ...prev, headquarters_city: event.target.value }))
              }
              required
            />
          </label>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={Boolean(manufacturerForm?.is_active)}
              onChange={(event) =>
                setManufacturerForm((prev) => ({ ...prev, is_active: event.target.checked }))
              }
            />
            Active
          </label>
          <div className="form-actions">
            <button type="submit" className="solid-button" disabled={isSavingManufacturer}>
              {isSavingManufacturer ? 'Saving...' : 'Save Manufacturer'}
            </button>
            <button
              type="button"
              className="ghost-button is-danger"
              disabled={isSavingManufacturer}
              onClick={onDeleteManufacturer}
            >
              Delete Manufacturer
            </button>
          </div>
        </form>
        {manufacturerActionError ? <p className="error-text">{manufacturerActionError}</p> : null}
      </div>

      <div className="products-section">
        <h3>Products</h3>
        <form className="editor-form" onSubmit={handleProductSubmit}>
          <label>
            Product Name
            <input
              value={productForm.product_name}
              onChange={(event) =>
                setProductForm((prev) => ({ ...prev, product_name: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Category
            <input
              value={productForm.category}
              onChange={(event) =>
                setProductForm((prev) => ({ ...prev, category: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Price
            <input
              type="number"
              step="0.01"
              min="0"
              value={productForm.price}
              onChange={(event) =>
                setProductForm((prev) => ({ ...prev, price: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Stock Quantity
            <input
              type="number"
              min="0"
              value={productForm.stock_quantity}
              onChange={(event) =>
                setProductForm((prev) => ({ ...prev, stock_quantity: event.target.value }))
              }
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={productForm.description}
              onChange={(event) =>
                setProductForm((prev) => ({ ...prev, description: event.target.value }))
              }
              rows={2}
            />
          </label>
          <div className="form-actions">
            <button type="submit" className="solid-button" disabled={isSavingProduct}>
              {isSavingProduct
                ? 'Saving...'
                : editingProductId
                  ? 'Update Product'
                  : 'Add Product'}
            </button>
            {editingProductId ? (
              <button
                type="button"
                className="ghost-button"
                onClick={() => {
                  setProductForm(emptyProductForm)
                  setEditingProductId(null)
                }}
              >
                Cancel Edit
              </button>
            ) : null}
          </div>
        </form>
        {productActionError ? <p className="error-text">{productActionError}</p> : null}
        <label className="search-control">
          Search Products
          <input
            className="search-input"
            value={productSearch}
            onChange={(event) => setProductSearch(event.target.value)}
            placeholder="Search by product, category, or description"
          />
        </label>
        <div className="form-actions">
          <button
            type="button"
            className="ghost-button"
            onClick={() => setProductSearch('')}
            disabled={!productSearch}
          >
            Clear Product Filter
          </button>
        </div>
        {detailsError ? (
          <p className="error-text">{detailsError}</p>
        ) : (
          <ProductList
            products={filteredProducts}
            isLoading={isLoadingProducts}
            onEdit={handleEditProduct}
            onDelete={handleDeleteProduct}
            deletingId={deletingProductId}
            onCategorySelect={setProductSearch}
          />
        )}
      </div>
    </section>
  )
}

export default ManufacturerDetail
