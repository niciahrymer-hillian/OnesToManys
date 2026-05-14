// [FILE] App_annotated_cp.jsx
// [WHY] Root React workspace with CRUD, analytics, pagination, and clickable analytics tabs.
// [EFFECT] Users can switch between distribution and product category coverage views, with a dedicated category coverage chart.

import { useEffect, useState } from 'react'
import ManufacturerDetail from './components/ManufacturerDetail'
import ManufacturerList from './components/ManufacturerList'
import {
  createManufacturer,
  createManufacturerProduct,
  deleteManufacturer,
  deleteManufacturerProduct,
  getManufacturer,
  getManufacturerProducts,
  getManufacturers,
  getProducts,
  updateManufacturer,
  updateManufacturerProduct,
} from './services/api'
import './App.css'

const emptyManufacturerCreateForm = {
  name: '',
  country: '',
  founded_year: '',
  headquarters_city: '',
  is_active: true,
}

const wholeNumberFormatter = new Intl.NumberFormat('en-US', {
  maximumFractionDigits: 0,
})

const currencyFormatter = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0,
})

function App() {
  const [manufacturers, setManufacturers] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [selectedManufacturer, setSelectedManufacturer] = useState(null)
  const [products, setProducts] = useState([])
  const [isLoadingManufacturers, setIsLoadingManufacturers] = useState(true)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)
  const [listError, setListError] = useState('')
  const [allProducts, setAllProducts] = useState([])
  const [isLoadingAllProducts, setIsLoadingAllProducts] = useState(true)
  const [productsError, setProductsError] = useState('')
  const [detailError, setDetailError] = useState('')
  const [manufacturerCreateForm, setManufacturerCreateForm] = useState(emptyManufacturerCreateForm)
  const [manufacturerActionError, setManufacturerActionError] = useState('')
  const [productActionError, setProductActionError] = useState('')
  const [isSavingManufacturer, setIsSavingManufacturer] = useState(false)
  const [isSavingProduct, setIsSavingProduct] = useState(false)
  const [manufacturerSearch, setManufacturerSearch] = useState('')
  const [datasetView, setDatasetView] = useState('manufacturers')
  const [chartMetric, setChartMetric] = useState('revenue')
  const [analyticsTab, setAnalyticsTab] = useState('distribution')
  const [manufacturerPage, setManufacturerPage] = useState(1)

  const ITEMS_PER_PAGE = 10

  const filteredManufacturers = manufacturers.filter((manufacturer) => {
    const term = manufacturerSearch.trim().toLowerCase()
    if (!term) {
      return true
    }
    return [manufacturer.name, manufacturer.country, manufacturer.headquarters_city]
      .join(' ')
      .toLowerCase()
      .includes(term)
  })

  const filteredAllProducts = allProducts.filter((product) => {
    const term = manufacturerSearch.trim().toLowerCase()
    if (!term) {
      return true
    }
    return [product.product_name, product.category, product.order_origin, product.sales_channel]
      .join(' ')
      .toLowerCase()
      .includes(term)
  })

  const manufacturerMaxPage = Math.ceil(filteredManufacturers.length / ITEMS_PER_PAGE)
  const paginatedManufacturers = filteredManufacturers.slice(
    (manufacturerPage - 1) * ITEMS_PER_PAGE,
    manufacturerPage * ITEMS_PER_PAGE,
  )

  const selectedProductCount = products.length
  const selectedUnitsSold = products.reduce((sum, product) => sum + Number(product.units_sold || 0), 0)
  const selectedRevenue = products.reduce((sum, product) => sum + Number(product.revenue || 0), 0)

  const statsByManufacturer = allProducts.reduce((accumulator, product) => {
    const manufacturerId = product.manufacturer_id
    if (!accumulator[manufacturerId]) {
      accumulator[manufacturerId] = {
        units_sold: 0,
        revenue: 0,
      }
    }

    accumulator[manufacturerId].units_sold += Number(product.units_sold || 0)
    accumulator[manufacturerId].revenue += Number(product.revenue || 0)
    return accumulator
  }, {})

  const rankedManufacturerStats = manufacturers
    .map((manufacturer) => {
      const stats = statsByManufacturer[manufacturer.manufacturer_id] || { units_sold: 0, revenue: 0 }
      return {
        manufacturer_id: manufacturer.manufacturer_id,
        name: manufacturer.name,
        units_sold: stats.units_sold,
        revenue: stats.revenue,
      }
    })
    .sort((left, right) => right[chartMetric] - left[chartMetric])

  const chartRows = rankedManufacturerStats.slice(0, 10)
  const chartMaxValue = chartRows[0]?.[chartMetric] || 0

  const channelDistribution = allProducts.reduce((accumulator, product) => {
    const channel = product.sales_channel || 'Unknown'
    accumulator[channel] = (accumulator[channel] || 0) + 1
    return accumulator
  }, {})

  const originDistribution = allProducts.reduce((accumulator, product) => {
    const origin = product.order_origin || 'Unknown'
    accumulator[origin] = (accumulator[origin] || 0) + 1
    return accumulator
  }, {})

  const allCategoriesByManufacturer = manufacturers.reduce((accumulator, manufacturer) => {
    const manufacturerProducts = allProducts.filter((p) => p.manufacturer_id === manufacturer.manufacturer_id)
    const categories = new Set(manufacturerProducts.map((p) => p.category))
    accumulator[manufacturer.manufacturer_id] = categories
    return accumulator
  }, {})

  const overlappingCategories = Array.from(
    Object.values(allCategoriesByManufacturer).reduce((accumulator, categorySet) => {
      const intersection = accumulator.size === 0 ? categorySet : new Set([...accumulator].filter((x) => categorySet.has(x)))
      return intersection
    }, new Set()),
  ).sort()

  const manufacturersPerCategory = Array.from(
    Object.values(allCategoriesByManufacturer).reduce((accumulator, categorySet) => {
      categorySet.forEach((category) => accumulator.add(category))
      return accumulator
    }, new Set()),
  )
    .map((category) => {
      const count = Object.values(allCategoriesByManufacturer).filter((categories) => categories.has(category))
        .length
      return { category, manufacturerCount: count, isOverlapping: count > 1 }
    })
    .sort((left, right) => right.manufacturerCount - left.manufacturerCount)

  const categoryCoverageRows = manufacturersPerCategory.map((item) => {
    const totalManufacturers = manufacturers.length || 1
    const coveragePercent = (item.manufacturerCount / totalManufacturers) * 100
    return {
      ...item,
      coveragePercent,
    }
  })

  async function loadManufacturers(preferredSelectedId = null) {
    try {
      setIsLoadingManufacturers(true)
      setListError('')
      const result = await getManufacturers()
      setManufacturers(result)
      const fallbackId = preferredSelectedId ?? selectedId
      const hasFallback = fallbackId && result.some((item) => item.manufacturer_id === fallbackId)
      setSelectedId(hasFallback ? fallbackId : (result[0]?.manufacturer_id ?? null))
    } catch (error) {
      setListError(error.message)
    } finally {
      setIsLoadingManufacturers(false)
    }
  }

  async function loadAllProducts() {
    try {
      setIsLoadingAllProducts(true)
      setProductsError('')
      const result = await getProducts()
      setAllProducts(result)
    } catch (error) {
      setProductsError(error.message)
    } finally {
      setIsLoadingAllProducts(false)
    }
  }

  async function loadDetails(manufacturerId) {
    if (!manufacturerId) {
      setSelectedManufacturer(null)
      setProducts([])
      return
    }

    try {
      setIsLoadingDetails(true)
      setDetailError('')
      const [manufacturerResult, productsResult] = await Promise.all([
        getManufacturer(manufacturerId),
        getManufacturerProducts(manufacturerId),
      ])
      setSelectedManufacturer(manufacturerResult)
      setProducts(productsResult)
    } catch (error) {
      setDetailError(error.message)
    } finally {
      setIsLoadingDetails(false)
    }
  }

  useEffect(() => {
    let isMounted = true

    async function initializeManufacturers() {
      await loadManufacturers()
      if (!isMounted) {
        return
      }
    }

    initializeManufacturers()
    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    loadAllProducts()
  }, [])

  useEffect(() => {
    let isMounted = true

    async function initializeDetails() {
      await loadDetails(selectedId)
      if (!isMounted) {
        return
      }
    }

    initializeDetails()
    return () => {
      isMounted = false
    }
  }, [selectedId])

  useEffect(() => {
    setManufacturerPage(1)
  }, [manufacturerSearch])

  async function handleCreateManufacturer(event) {
    event.preventDefault()
    setManufacturerActionError('')

    try {
      setIsSavingManufacturer(true)
      const created = await createManufacturer({
        ...manufacturerCreateForm,
        founded_year: Number(manufacturerCreateForm.founded_year),
      })
      setManufacturerCreateForm(emptyManufacturerCreateForm)
      await loadManufacturers(created.manufacturer_id)
    } catch (error) {
      setManufacturerActionError(error.message)
    } finally {
      setIsSavingManufacturer(false)
    }
  }

  async function handleUpdateManufacturer(payload) {
    if (!selectedId) {
      return
    }

    setManufacturerActionError('')

    try {
      setIsSavingManufacturer(true)
      await updateManufacturer(selectedId, payload)
      await Promise.all([loadManufacturers(selectedId), loadDetails(selectedId)])
    } catch (error) {
      setManufacturerActionError(error.message)
    } finally {
      setIsSavingManufacturer(false)
    }
  }

  async function handleDeleteManufacturer() {
    if (!selectedId) {
      return
    }

    if (!window.confirm('Delete this manufacturer and all of its products?')) {
      return
    }

    setManufacturerActionError('')
    try {
      setIsSavingManufacturer(true)
      await deleteManufacturer(selectedId)
      await loadManufacturers()
    } catch (error) {
      setManufacturerActionError(error.message)
    } finally {
      setIsSavingManufacturer(false)
    }
  }

  async function handleCreateProduct(payload) {
    if (!selectedId) {
      return
    }

    setProductActionError('')
    try {
      setIsSavingProduct(true)
      await createManufacturerProduct(selectedId, payload)
      await loadDetails(selectedId)
    } catch (error) {
      setProductActionError(error.message)
    } finally {
      setIsSavingProduct(false)
    }
  }

  async function handleUpdateProduct(productId, payload) {
    if (!selectedId) {
      return
    }

    setProductActionError('')
    try {
      setIsSavingProduct(true)
      await updateManufacturerProduct(selectedId, productId, payload)
      await loadDetails(selectedId)
    } catch (error) {
      setProductActionError(error.message)
    } finally {
      setIsSavingProduct(false)
    }
  }

  async function handleDeleteProduct(productId) {
    if (!selectedId) {
      return
    }

    setProductActionError('')
    try {
      setIsSavingProduct(true)
      await deleteManufacturerProduct(selectedId, productId)
      await loadDetails(selectedId)
    } catch (error) {
      setProductActionError(error.message)
    } finally {
      setIsSavingProduct(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-topline">
          <p className="eyebrow">Phase 3 · React Frontend</p>
          <span className="mode-badge">Mode: React</span>
        </div>
        <h1>Manufacturer and Product Workspace</h1>
        <p className="subtitle">
          Select a manufacturer to inspect its details and product catalog.
        </p>
        <div className="react-page-links" aria-label="Quick navigation">
          <a className="react-link" href="http://127.0.0.1:8090/frontend-launcher/index.html" target="_blank" rel="noreferrer">
            Unified Launcher
          </a>
          <a className="react-link" href="http://127.0.0.1:8080/index.html" target="_blank" rel="noreferrer">
            Vanilla Home
          </a>
        </div>
        <div className="summary-strip" aria-label="Relationship summary">
          <article className="summary-chip">
            <p className="chip-label">Manufacturers Loaded</p>
            <p className="chip-value">{manufacturers.length}</p>
          </article>
          <article className="summary-chip">
            <p className="chip-label">Search Results</p>
            <p className="chip-value">{filteredManufacturers.length}</p>
          </article>
          <article className="summary-chip">
            <p className="chip-label">Products For Selected Manufacturer</p>
            <p className="chip-value">{selectedId ? selectedProductCount : 0}</p>
          </article>
          <article className="summary-chip">
            <p className="chip-label">Units Sold</p>
            <p className="chip-value">{selectedId ? selectedUnitsSold : 0}</p>
          </article>
          <article className="summary-chip">
            <p className="chip-label">Revenue</p>
            <p className="chip-value">${selectedId ? selectedRevenue.toFixed(2) : '0.00'}</p>
          </article>
        </div>

        <section className="analytics-panel" aria-label="Manufacturer sales visualization">
          <div className="analytics-header">
            <div>
              <h2>Manufacturer Sales Chart</h2>
              <p>Bar charts are best for comparing all manufacturers side by side.</p>
            </div>
            <div className="analytics-switch" role="tablist" aria-label="Sales metric">
              <button
                type="button"
                className={`analytics-switch-button${chartMetric === 'revenue' ? ' is-active' : ''}`}
                onClick={() => setChartMetric('revenue')}
              >
                Revenue
              </button>
              <button
                type="button"
                className={`analytics-switch-button${chartMetric === 'units_sold' ? ' is-active' : ''}`}
                onClick={() => setChartMetric('units_sold')}
              >
                Units Sold
              </button>
            </div>
          </div>

          {isLoadingAllProducts ? (
            <p className="status-text">Loading chart data...</p>
          ) : productsError ? (
            <p className="error-text">{productsError}</p>
          ) : chartRows.length === 0 ? (
            <p className="status-text">No seeded stats available yet.</p>
          ) : (
            <ul className="analytics-chart-list">
              {chartRows.map((row) => {
                const value = row[chartMetric]
                const width = chartMaxValue > 0 ? (value / chartMaxValue) * 100 : 0
                return (
                  <li key={row.manufacturer_id} className="analytics-chart-row">
                    <div className="analytics-chart-head">
                      <span className="analytics-chart-name">{row.name}</span>
                      <span className="analytics-chart-value">
                        {chartMetric === 'revenue'
                          ? currencyFormatter.format(value)
                          : wholeNumberFormatter.format(value)}
                      </span>
                    </div>
                    <div className="analytics-chart-track" aria-hidden="true">
                      <div
                        className="analytics-chart-fill"
                        style={{ width: `${Math.max(width, value > 0 ? 2 : 0)}%` }}
                      />
                    </div>
                    <p className="analytics-chart-meta">
                      Units: {wholeNumberFormatter.format(row.units_sold)} · Revenue:{' '}
                      {currencyFormatter.format(row.revenue)}
                    </p>
                  </li>
                )
              })}
            </ul>
          )}
        </section>

        <div className="analytics-tabs" role="tablist" aria-label="Analytics views">
          <button
            type="button"
            className={`analytics-tab-button${analyticsTab === 'distribution' ? ' is-active' : ''}`}
            onClick={() => setAnalyticsTab('distribution')}
            aria-selected={analyticsTab === 'distribution'}
          >
            Distribution Analysis
          </button>
          <button
            type="button"
            className={`analytics-tab-button${analyticsTab === 'coverage' ? ' is-active' : ''}`}
            onClick={() => setAnalyticsTab('coverage')}
            aria-selected={analyticsTab === 'coverage'}
          >
            Product Category Coverage
          </button>
        </div>

        {analyticsTab === 'distribution' ? (
          <section className="distribution-panel" aria-label="Sales channel and origin distribution">
            <h2>Distribution Analysis</h2>
            <div className="distribution-grid">
              <div className="distribution-card">
                <h3>By Sales Channel</h3>
                <ul className="distribution-list">
                  {Object.entries(channelDistribution)
                    .sort((left, right) => right[1] - left[1])
                    .map(([channel, count]) => (
                      <li key={channel}>
                        <span className="distribution-label">{channel}</span>
                        <span className="distribution-bar">
                          <span
                            className="distribution-fill"
                            style={{ width: `${(count / allProducts.length) * 100}%` }}
                          />
                        </span>
                        <span className="distribution-count">{count}</span>
                      </li>
                    ))}
                </ul>
              </div>
              <div className="distribution-card">
                <h3>By Order Origin</h3>
                <ul className="distribution-list">
                  {Object.entries(originDistribution)
                    .sort((left, right) => right[1] - left[1])
                    .map(([origin, count]) => (
                      <li key={origin}>
                        <span className="distribution-label">{origin}</span>
                        <span className="distribution-bar">
                          <span
                            className="distribution-fill"
                            style={{ width: `${(count / allProducts.length) * 100}%` }}
                          />
                        </span>
                        <span className="distribution-count">{count}</span>
                      </li>
                    ))}
                </ul>
              </div>
            </div>
          </section>
        ) : (
          <section className="overlapping-panel" aria-label="Product categories across manufacturers">
            <h2>Product Category Coverage Chart</h2>
            <p className="overlapping-intro">
              Shared categories appear in {overlappingCategories.length} or more manufacturers.
            </p>
            <ul className="coverage-chart-list">
              {categoryCoverageRows.map((item) => (
                <li key={item.category} className="coverage-chart-row">
                  <div className="coverage-chart-head">
                    <span className="coverage-chart-name">{item.category}</span>
                    <span className="coverage-chart-value">
                      {item.manufacturerCount}/{manufacturers.length} ({item.coveragePercent.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="coverage-chart-track" aria-hidden="true">
                    <div
                      className="coverage-chart-fill"
                      style={{ width: `${Math.max(item.coveragePercent, item.manufacturerCount > 0 ? 3 : 0)}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
            <ul className="overlapping-list">
              {categoryCoverageRows.map((item) => (
                <li key={`${item.category}-badge`} className={item.isOverlapping ? 'is-overlapping' : ''}>
                  <span className="overlapping-badge">{item.manufacturerCount}</span>
                  <span className="overlapping-label">{item.category}</span>
                  {item.isOverlapping && <span className="overlapping-tag">Shared</span>}
                </li>
              ))}
            </ul>
          </section>
        )}
      </header>

      <main className="workspace-grid">
        <section className="list-panel">
          <div className="dataset-switcher" role="tablist" aria-label="Dataset views">
            <button
              type="button"
              className={`dataset-switch${datasetView === 'manufacturers' ? ' is-active' : ''}`}
              onClick={() => setDatasetView('manufacturers')}
            >
              Manufacturers ({filteredManufacturers.length})
            </button>
            <button
              type="button"
              className={`dataset-switch${datasetView === 'products' ? ' is-active' : ''}`}
              onClick={() => setDatasetView('products')}
            >
              Products ({filteredAllProducts.length})
            </button>
          </div>
          <form className="editor-form" onSubmit={handleCreateManufacturer}>
            <label>
              Name
              <input
                value={manufacturerCreateForm.name}
                onChange={(event) =>
                  setManufacturerCreateForm((prev) => ({ ...prev, name: event.target.value }))
                }
                required
              />
            </label>
            <label>
              Country
              <input
                value={manufacturerCreateForm.country}
                onChange={(event) =>
                  setManufacturerCreateForm((prev) => ({ ...prev, country: event.target.value }))
                }
                required
              />
            </label>
            <label>
              Founded Year
              <input
                type="number"
                value={manufacturerCreateForm.founded_year}
                onChange={(event) =>
                  setManufacturerCreateForm((prev) => ({ ...prev, founded_year: event.target.value }))
                }
                required
              />
            </label>
            <label>
              Headquarters City
              <input
                value={manufacturerCreateForm.headquarters_city}
                onChange={(event) =>
                  setManufacturerCreateForm((prev) => ({ ...prev, headquarters_city: event.target.value }))
                }
                required
              />
            </label>
            <button type="submit" className="solid-button" disabled={isSavingManufacturer}>
              {isSavingManufacturer ? 'Saving...' : 'Add Manufacturer'}
            </button>
          </form>
          {manufacturerActionError ? <p className="error-text">{manufacturerActionError}</p> : null}
          <label className="search-control">
            Search {datasetView === 'manufacturers' ? 'Manufacturers' : 'Products'}
            <input
              className="search-input"
              value={manufacturerSearch}
              onChange={(event) => setManufacturerSearch(event.target.value)}
              placeholder={
                datasetView === 'manufacturers'
                  ? 'Search by name, country, or city'
                  : 'Search by product, category, origin, or channel'
              }
            />
          </label>
          {listError ? (
            <p className="error-text">{listError}</p>
          ) : productsError ? (
            <p className="error-text">{productsError}</p>
          ) : datasetView === 'manufacturers' ? (
            <>
              <ManufacturerList
                manufacturers={paginatedManufacturers}
                selectedId={selectedId}
                onSelect={setSelectedId}
                onApplySearch={setManufacturerSearch}
                isLoading={isLoadingManufacturers}
              />
              {manufacturerMaxPage > 1 && (
                <div className="pagination-controls" role="navigation" aria-label="Manufacturer list pagination">
                  <button
                    type="button"
                    className="pagination-button"
                    onClick={() => setManufacturerPage((prev) => Math.max(prev - 1, 1))}
                    disabled={manufacturerPage === 1}
                  >
                    ← Previous
                  </button>
                  <span className="pagination-info">
                    Page {manufacturerPage} of {manufacturerMaxPage}
                  </span>
                  <button
                    type="button"
                    className="pagination-button"
                    onClick={() => setManufacturerPage((prev) => Math.min(prev + 1, manufacturerMaxPage))}
                    disabled={manufacturerPage === manufacturerMaxPage}
                  >
                    Next →
                  </button>
                </div>
              )}
            </>
          ) : isLoadingAllProducts ? (
            <p className="status-text">Loading products...</p>
          ) : filteredAllProducts.length === 0 ? (
            <p className="status-text">No products found.</p>
          ) : (
            <ul className="dataset-button-list" aria-label="All products list">
              {filteredAllProducts.map((product) => {
                const manufacturer = manufacturers.find(
                  (item) => item.manufacturer_id === product.manufacturer_id,
                )
                return (
                  <li key={product.product_id}>
                    <button
                      type="button"
                      className="dataset-button"
                      onClick={() => {
                        setDatasetView('manufacturers')
                        setSelectedId(product.manufacturer_id)
                        setManufacturerSearch('')
                      }}
                    >
                      <span className="dataset-button-title">
                        #{product.product_id} {product.product_name}
                      </span>
                      <span className="dataset-button-meta">
                        {product.category} · {manufacturer?.name || `Manufacturer ${product.manufacturer_id}`}
                      </span>
                      <span className="dataset-button-meta">
                        {product.order_origin} · {product.sales_channel}
                      </span>
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </section>

        <ManufacturerDetail
          manufacturer={selectedManufacturer}
          products={products}
          isLoadingProducts={isLoadingDetails}
          detailsError={detailError}
          onUpdateManufacturer={handleUpdateManufacturer}
          onDeleteManufacturer={handleDeleteManufacturer}
          onCreateProduct={handleCreateProduct}
          onUpdateProduct={handleUpdateProduct}
          onDeleteProduct={handleDeleteProduct}
          isSavingManufacturer={isSavingManufacturer}
          isSavingProduct={isSavingProduct}
          manufacturerActionError={manufacturerActionError}
          productActionError={productActionError}
        />
      </main>

      <footer className="app-footer">
        <p>
          API base: <code>http://127.0.0.1:5000/api</code>
        </p>
      </footer>
    </div>
  )
}

export default App
