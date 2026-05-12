import { useEffect, useState } from 'react'
import ManufacturerDetail from './components/ManufacturerDetail'
import ManufacturerList from './components/ManufacturerList'
import {
  getManufacturer,
  getManufacturerProducts,
  getManufacturers,
} from './services/api'
import './App.css'

function App() {
  const [manufacturers, setManufacturers] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [selectedManufacturer, setSelectedManufacturer] = useState(null)
  const [products, setProducts] = useState([])
  const [isLoadingManufacturers, setIsLoadingManufacturers] = useState(true)
  const [isLoadingDetails, setIsLoadingDetails] = useState(false)
  const [listError, setListError] = useState('')
  const [detailError, setDetailError] = useState('')

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
