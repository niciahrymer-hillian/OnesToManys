// [FILE] ProductList_annotated_cp.jsx
// [WHY] Represents detail records (products) in tabular structure.
// [EFFECT] Users can quickly scan category, price, and stock values.

function ProductList({ products, isLoading, onEdit, onDelete, deletingId, onCategorySelect }) {
  if (isLoading) {
    return <p className="status-text">Loading products...</p>
  }

  if (products.length === 0) {
    return <p className="status-text">This manufacturer does not have products yet.</p>
  }

  return (
    <div className="product-grid" role="table" aria-label="Products">
      <div className="product-row product-row-head" role="row">
        <span role="columnheader">Product</span>
        <span role="columnheader">Category</span>
        <span role="columnheader">Price</span>
        <span role="columnheader">Stock</span>
        <span role="columnheader">Actions</span>
      </div>
      {products.map((product) => (
        <div className="product-row" role="row" key={product.product_id}>
          <span role="cell">
            <button type="button" className="inline-link-button" onClick={() => onEdit(product)}>
              #{product.product_id} {product.product_name}
            </button>
          </span>
          <span role="cell">
            <button
              type="button"
              className="inline-link-button"
              onClick={() => onCategorySelect?.(product.category)}
            >
              {product.category}
            </button>
          </span>
          <span role="cell">${Number(product.price).toFixed(2)}</span>
          <span role="cell">{product.stock_quantity}</span>
          <span role="cell" className="product-actions">
            <button type="button" className="inline-button" onClick={() => onEdit(product)}>
              Edit
            </button>
            <button
              type="button"
              className="inline-button is-danger"
              onClick={() => onDelete(product.product_id)}
              disabled={deletingId === product.product_id}
            >
              {deletingId === product.product_id ? 'Deleting...' : 'Delete'}
            </button>
          </span>
        </div>
      ))}
    </div>
  )
}

export default ProductList
