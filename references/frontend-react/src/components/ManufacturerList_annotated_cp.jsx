// [FILE] ManufacturerList_annotated_cp.jsx
// [WHY] Shows selectable master entities in the list-detail layout.
// [EFFECT] User can pick one manufacturer to drive detail/product data loading.

function ManufacturerList({ manufacturers, selectedId, onSelect, isLoading }) {
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
            <button
              type="button"
              className={`manufacturer-card${isSelected ? ' is-selected' : ''}`}
              onClick={() => onSelect(manufacturer.manufacturer_id)}
            >
              <span className="manufacturer-name">{manufacturer.name}</span>
              <span className="manufacturer-meta">
                {manufacturer.country} · Founded {manufacturer.founded_year}
              </span>
            </button>
          </li>
        )
      })}
    </ul>
  )
}

export default ManufacturerList
