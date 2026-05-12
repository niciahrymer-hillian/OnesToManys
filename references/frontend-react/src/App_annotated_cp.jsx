// [FILE] App_annotated_cp.jsx
// [WHY] Root container for Phase 3 React UI.
// [EFFECT] Coordinates manufacturer selection and product detail loading.

// [IMPORT] React state/effect hooks for async data flow.
import { useEffect, useState } from 'react'
// [IMPORT] UI components.
import ManufacturerDetail from './components/ManufacturerDetail'
import ManufacturerList from './components/ManufacturerList'
// [IMPORT] API service layer.
import {
  getManufacturer,
  getManufacturerProducts,
  getManufacturers,
} from './services/api'
import './App.css'

// [FUNCTION][COMPONENT] Application shell.
function App() {
  // [STATE] List panel data.
  const [manufacturers, setManufacturers] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  // [STATE] Detail panel data.
  const [selectedManufacturer, setSelectedManufacturer] = useState(null)
  const [products, setProducts] = useState([])
  // [STATE] UX states.
  const [isLoadingManufacturers, setIsLoadingManufacturers] = useState(true)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)
  const [listError, setListError] = useState('')
  const [detailError, setDetailError] = useState('')

  // [EFFECT] Load the manufacturer list at app startup.
  useEffect(() => {
    let isMounted = true

    async function loadManufacturers() {
      try {
        setIsLoadingManufacturers(true)
        const result = await getManufacturers()
        if (!isMounted) {
          return
        }
        setManufacturers(result)
        // [WHY] Auto-select first manufacturer for immediate detail view.
        if (result.length > 0) {
          setSelectedId(result[0].manufacturer_id)
        }
      } catch (error) {
        if (isMounted) {
          setListError(error.message)
        }
      } finally {
        if (isMounted) {
          setIsLoadingManufacturers(false)
        }
      }
    }

    loadManufacturers()
    return () => {
      isMounted = false
    }
  }, [])

  // [EFFECT] Reload detail and products whenever selection changes.
  useEffect(() => {
    let isMounted = true

    async function loadDetails() {
      if (!selectedId) {
        setSelectedManufacturer(null)
        setProducts([])
        return
      }

      try {
        setIsLoadingDetails(true)
        setDetailError('')
        const [manufacturerResult, productsResult] = await Promise.all([
          getManufacturer(selectedId),
          getManufacturerProducts(selectedId),
        ])
        if (!isMounted) {
          return
        }
        setSelectedManufacturer(manufacturerResult)
        setProducts(productsResult)
      } catch (error) {
        if (isMounted) {
          setDetailError(error.message)
        }
      } finally {
        if (isMounted) {
          setIsLoadingDetails(false)
        }
      }
    }

    loadDetails()
    return () => {
      isMounted = false
    }
  }, [selectedId])

  // [RETURN] Two-column layout: list panel + detail panel.
  return (
    <div className="app-shell">
      <header className="app-header">
        <p className="eyebrow">Phase 3 · React Frontend</p>
        <h1>Manufacturer and Product Workspace</h1>
        <p className="subtitle">
          Select a manufacturer to inspect its details and product catalog.
        </p>
      </header>

      <main className="workspace-grid">
        <section className="list-panel">
          <h2>Manufacturers</h2>
          {listError ? (
            <p className="error-text">{listError}</p>
          ) : (
            <ManufacturerList
              manufacturers={manufacturers}
              selectedId={selectedId}
              onSelect={setSelectedId}
              isLoading={isLoadingManufacturers}
            />
          )}
        </section>

        <ManufacturerDetail
          manufacturer={selectedManufacturer}
          products={products}
          isLoadingProducts={isLoadingDetails}
          detailsError={detailError}
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
