import ProductList from './ProductList'

function ManufacturerDetail({ manufacturer, products, isLoadingProducts, detailsError }) {
  if (!manufacturer) {
    return (
      <section className="detail-panel">
        <p className="status-text">Choose a manufacturer to view details and products.</p>
      </section>
    )
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
      </dl>

      <div className="products-section">
        <h3>Products</h3>
        {detailsError ? (
          <p className="error-text">{detailsError}</p>
        ) : (
          <ProductList products={products} isLoading={isLoadingProducts} />
        )}
      </div>
    </section>
  )
}

export default ManufacturerDetail
