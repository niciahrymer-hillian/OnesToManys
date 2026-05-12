// [FILE] main_annotated_cp.jsx
// [WHY] Browser entrypoint for React application.
// [EFFECT] Mounts App into root DOM node with StrictMode checks.

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
