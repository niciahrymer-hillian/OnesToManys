# HTTPS Setup Guide

Your application currently runs on HTTP. Here are two approaches to enable HTTPS for development and production.

## Option 1: Quick Self-Signed HTTPS (Development)

### Using Vite's Built-in SSL Plugin

1. **Install the plugin:**
```bash
cd frontend-react
npm install --save-dev @vitejs/plugin-basic-ssl
```

2. **Update `vite.config.js`:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

export default defineConfig({
  plugins: [react(), basicSsl()],
  server: {
    https: true,
    port: 5173,
    host: '127.0.0.1'
  }
})
```

3. **Run dev server:**
```bash
npm run dev
```

4. **Access via:**
```
https://127.0.0.1:5173
```

**Note:** Browser will show certificate warning - click "Advanced" → "Proceed" to accept the self-signed cert.

---

## Option 2: Professional Certificates (Production/mkcert)

### Using mkcert for Trusted Local Certificates

1. **Install mkcert** (macOS):
```bash
brew install mkcert
brew install nss  # Required for Firefox
```

2. **Create local CA:**
```bash
mkcert -install
```

3. **Generate certificates:**
```bash
cd /Users/nicky/Projects/OnesToManys
mkcert -key-file=cert.key -cert-file=cert.pem localhost 127.0.0.1
```

4. **Update `vite.config.js`:**
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'
import path from 'path'

const __dirname = path.dirname(new URL(import.meta.url).pathname)

export default defineConfig({
  plugins: [react()],
  server: {
    https: {
      key: fs.readFileSync(path.resolve(__dirname, 'cert.key')),
      cert: fs.readFileSync(path.resolve(__dirname, 'cert.pem'))
    },
    port: 5173,
    host: '127.0.0.1'
  }
})
```

5. **Run dev server:**
```bash
npm run dev
```

6. **Access via:**
```
https://127.0.0.1:5173
```

**Advantage:** Browser shows green lock (trusted certificate)

---

## Option 3: Backend HTTPS (Flask)

### Enable HTTPS on Flask API

1. **Install pyopenssl:**
```bash
pip install pyopenssl
```

2. **Update `app.py`:**
```python
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',
        port=5000,
        ssl_context=('cert.pem', 'cert.key'),  # Use same certs from Option 2
        debug=True
    )
```

3. **Update `services/api.js`** to use HTTPS:
```javascript
const API_BASE = 'https://127.0.0.1:5000/api'
```

---

## Recommendation

- **Development:** Use **Option 1** (@vitejs/plugin-basic-ssl) - simplest, no setup
- **Both Frontend + Backend:** Use **Option 2** + **Option 3** - more professional
- **Production:** Use proper SSL certificates from a trusted CA (e.g., Let's Encrypt, AWS)

---

## Current Status

✅ Frontend (Vite) - Ready for HTTPS  
✅ Backend (Flask) - Can enable HTTPS  
✅ Database - SQLite (no HTTPS needed)  
✅ Pagination - Just added (shows 10 items per page)

Choose an option above and let me know which you'd like to implement!
