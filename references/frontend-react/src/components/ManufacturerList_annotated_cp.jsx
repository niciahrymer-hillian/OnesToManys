// [FILE] ManufacturerList_annotated_cp.jsx
// [WHY] Shows selectable master entities in the list-detail layout.
// [EFFECT] User can pick one manufacturer to drive detail/product data loading.

function ManufacturerList({ manufacturers, selectedId, onSelect, onApplySearch, isLoading }) {
  // [GUARD] Loading and empty states keep UI clear.
  if (isLoading) {
    return <p className="status-text">Loading manufacturers...</p>
  }

  if (manufacturers.length === 0) {
    return <p className="status-text">No manufacturers found.</p>
  }

  return (
    <ul className="manufacturer-list" aria-label="Manufacturer list">
      {manufacturers.map((manufacturer) => {
        const isSelected = manufacturer.manufacturer_id === selectedId
        return (
          <li key={manufacturer.manufacturer_id}>
            <div className={`manufacturer-card${isSelected ? ' is-selected' : ''}`}>
              <button
                type="button"
                className="attr-button manufacturer-id"
                onClick={() => onSelect(manufacturer.manufacturer_id)}
              >
                #{manufacturer.manufacturer_id}
              </button>
              <button
                type="button"
                className="attr-button manufacturer-name"
                onClick={() => onSelect(manufacturer.manufacturer_id)}
              >
                {manufacturer.name}
              </button>
              <span className="manufacturer-meta">
                <button
                  type="button"
                  className="attr-button"
                  onClick={() => onApplySearch(manufacturer.country)}
                >
                  {manufacturer.country}
                </button>
                {' · Founded '}
                <button
                  type="button"
                  className="attr-button"
                  onClick={() => onApplySearch(String(manufacturer.founded_year))}
                >
                  {manufacturer.founded_year}
                </button>
              </span>
            </div>
          </li>
        )
      })}
    </ul>
  )
}

export default ManufacturerList
