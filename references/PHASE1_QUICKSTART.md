# Phase 1 Quick Start Guide

## Backend Manual Recreation (Canonical Command Log)

Use this exact sequence to recreate backend setup and verification manually.

### 0. Enter Project Root
```bash
cd /Users/nicky/Projects/OnesToManys
pwd
```

Expected output:
- `/Users/nicky/Projects/OnesToManys`

### 1. Create and Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
which python
```

Expected output:
- Python path should be inside project venv, for example:
  - `/Users/nicky/Projects/OnesToManys/venv/bin/python`

### 2. Install Backend Dependencies
```bash
pip install --upgrade pip
pip install flask flask-sqlalchemy flask-cors pytest
```

### 3. Validate Python Imports
```bash
python -c "import flask, flask_sqlalchemy, flask_cors, pytest; print('backend deps ok')"

---

```

Expected output:
- `backend deps ok`

### 4. Run Backend Test Suite (Canonical)
```bash
/Users/nicky/Projects/OnesToManys/venv/bin/python -m pytest
```

Expected output:
- `54 passed`
- Warnings are acceptable (`LegacyAPIWarning` from SQLAlchemy Query.get)
- `* Serving Flask app 'app'`
- `* Running on http://127.0.0.1:5000`
Important guardrail:
- If you see fixture errors from files in `references/`, verify `pytest.ini` includes:
  - `testpaths = tests`
  - `norecursedirs = references`

### 5. Start Flask Backend Server
```bash
/Users/nicky/Projects/OnesToManys/venv/bin/python app.py
```

Expected server log lines:
- `* Debug mode: on`
- `* Running on http://127.0.0.1:5000`

### 6. Verify API Health and Core Endpoints (Second Terminal)
```bash
curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/api/manufacturers
curl http://127.0.0.1:5000/api/products
```

Expected health response:
- `Serving HTTP on ... port 8080`

### 6b. Run Phase 2 curl Checks
With the Flask server still running in one terminal:

```bash
chmod +x scripts/phase2_curl_checks.sh
./scripts/phase2_curl_checks.sh
```

What this verifies:
- nested one-to-many route creation and retrieval
- JSON export at `/api/export/json`
- JSON import at `/api/import/json`

Expected last line:
- `python3 -m http.server 8080 in frontend-vanilla`

If you need to show this as project evidence, keep:
- the exact command you ran
- the script output ending in `curl Phase 2 checks passed`
- any exported `export.json` file you used for the import step

Important note:
- curl covers the endpoint-testing intent.
- `Ctrl+C`

### 7. Stop Server
In the server terminal, press:
- `Ctrl+C`

---

## 1. Setup Environment (First Time Only)

### Create Python Virtual Environment
```bash
cd /Users/nicky/Projects/OnesToManys
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies
```bash
pip install flask flask-sqlalchemy flask-cors pytest
```

Or from requirements.txt (if created):
```bash
pip install -r requirements.txt
```

**Verify Installation:**
```bash
python3 -c "import flask; import flask_sqlalchemy; import pytest; print('All packages installed!')"
```

---

## 2. Initialize Database

### Option A: Auto-Create from ORM (Recommended for Dev)
```bash
python3 << 'EOF'
from app import app, db
with app.app_context():
    db.create_all()
    print("✓ Database created successfully (data.db)")
EOF
```

### Option B: Use SQL Schema Files
```bash
# Create schema
sqlite3 data.db < schema.sql

# Add seed data
sqlite3 data.db < seed_data.sql

echo "✓ Database initialized with seed data"
```

**Verify Database Created:**
```bash
ls -lh data.db
sqlite3 data.db ".tables"  # Should show: manufacturers products
```

---

## 3. Run Tests (Validate Phase 1)

### Run All Tests
```bash
pytest tests/ -v
```

**Expected Output:**
```
tests/unit/test_models.py::TestManufacturerModel::test_should_create_manufacturer_with_valid_data PASSED
tests/unit/test_models.py::TestManufacturerModel::test_should_serialize_manufacturer_to_dict PASSED
...
======================== 40 passed in 0.42s ========================
```

### Run Specific Test Suites
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Manufacturers API tests
pytest tests/integration/test_manufacturers_api.py -v

# Products API tests
pytest tests/integration/test_products_api.py -v
```

### Debug a Single Test
```bash
pytest tests/integration/test_manufacturers_api.py::TestManufacturerPostEndpoint::test_should_create_manufacturer_with_valid_data -v -s
```

**Troubleshooting Tests:**
- If tests fail: Check that `app.py`, `models.py`, and `conftest.py` are in correct locations
- If import errors: Activate venv (`source venv/bin/activate`)
- If fixture errors: Ensure `tests/__init__.py` and `tests/*/init__.py` exist

---

## 4. Run Flask API Server

### Start Development Server
```bash
# Activate venv first
source venv/bin/activate

# Start Flask (runs on http://localhost:5000)
python3 app.py
```

**Output Should Show:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

## 4b. Open Complete Site From One URL (Unified Launcher)

From project root, run:

```bash
cd /Users/nicky/Projects/OnesToManys
python3 -m http.server 8090
```

Then open:

- `http://127.0.0.1:8090/frontend-launcher/index.html`

This launcher provides one control URL with embedded views for:
- React primary app (`5173` or `5174` fallback)
- Vanilla archive/demo pages (`8080`)

### Test Health Check
```bash
curl http://localhost:5000/
# Expected: {"message":"Manufacturer-Products API is running"}
```

### Keep Terminal Open
The server runs in foreground. Open another terminal to make requests.

---

## 5. Test API Manually (curl or Postman)

### Terminal 1: Keep Flask Running
```bash
python3 app.py
```

### Terminal 2: Test Endpoints

#### Health Check
```bash
curl http://localhost:5000/
```

#### Create Manufacturer
```bash
curl -X POST http://localhost:5000/api/manufacturers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sony",
    "country": "Japan",
    "founded_year": 1946,
    "headquarters_city": "Tokyo"
  }'
```

Expected response:
```json
{
  "manufacturer_id": 1,
  "name": "Sony",
  "country": "Japan",
  "founded_year": 1946,
  "headquarters_city": "Tokyo",
  "is_active": true,
  "created_at": "2024-01-XX HH:MM:SS.XXXXX",
  "updated_at": "2024-01-XX HH:MM:SS.XXXXX"
}
```

#### Get All Manufacturers
```bash
curl http://localhost:5000/api/manufacturers
```

#### Get Products For One Manufacturer
```bash
curl http://localhost:5000/api/manufacturers/1/products
```

#### Create Product
```bash
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer_id": 1,
    "product_name": "PlayStation 5",
    "category": "Gaming Console",
    "price": 499.99,
    "stock_quantity": 100,
    "description": "Next-gen gaming console"
  }'
```

#### Export All Data To JSON
```bash
curl http://localhost:5000/api/export/json -o export.json
cat export.json
```

#### Import Data From JSON
```bash
curl -X POST http://localhost:5000/api/import/json \
  -H "Content-Type: application/json" \
  --data-binary @export.json
```

#### Get All Products
```bash
curl http://localhost:5000/api/products
```

#### Get Single Product
```bash
curl http://localhost:5000/api/products/1
```

#### Update Product
```bash
curl -X PUT http://localhost:5000/api/products/1 \
  -H "Content-Type: application/json" \
  -d '{"stock_quantity": 50}'
```

#### Delete Product
```bash
curl -X DELETE http://localhost:5000/api/products/1
```

#### Delete Manufacturer (Cascade)
```bash
curl -X DELETE http://localhost:5000/api/manufacturers/1
```

This deletes the manufacturer AND all its products automatically (cascade delete).

---

## 6. Verify Cascade Delete Works

### Step 1: Create Manufacturer
```bash
curl -X POST http://localhost:5000/api/manufacturers \
  -H "Content-Type: application/json" \
  -d '{"name":"Apple","country":"USA","founded_year":1976}'
```

Response: `{"manufacturer_id": 1, ...}`

### Step 2: Create Products for That Manufacturer
```bash
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"manufacturer_id":1,"product_name":"iPhone","price":999.99,"stock_quantity":50}'

curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"manufacturer_id":1,"product_name":"iPad","price":599.99,"stock_quantity":30}'
```

### Step 3: Verify Products Exist
```bash
curl http://localhost:5000/api/products
# Should list 2 products with manufacturer_id=1
```

### Step 4: Delete Manufacturer
```bash
curl -X DELETE http://localhost:5000/api/manufacturers/1
```

### Step 5: Verify Products Deleted
```bash
curl http://localhost:5000/api/products
# Should be empty (both products cascaded)
```

✅ **Cascade delete working correctly!**

---

## 7. Check Database File

### View Database Contents
```bash
# List tables
sqlite3 data.db ".tables"

# Show manufacturers
sqlite3 data.db "SELECT * FROM manufacturers;"

# Show products
sqlite3 data.db "SELECT * FROM products;"

# Show schema
sqlite3 data.db ".schema manufacturers"
sqlite3 data.db ".schema products"
```

### Verify Seed Relationship Scale (12 manufacturers x 30 products)
```bash
# Total manufacturers (expected: 12)
sqlite3 data.db "SELECT COUNT(*) AS manufacturer_count FROM manufacturers;"

# Total products (expected: 360)
sqlite3 data.db "SELECT COUNT(*) AS product_count FROM products;"

# Per-manufacturer product counts (expected: 30 each)
sqlite3 data.db "
SELECT
  m.manufacturer_id,
  m.name,
  COUNT(p.product_id) AS product_count
FROM manufacturers m
LEFT JOIN products p ON p.manufacturer_id = m.manufacturer_id
GROUP BY m.manufacturer_id, m.name
ORDER BY m.manufacturer_id;
"
```

Expected relationship evidence:
- manufacturer count = `12`
- product count = `360`
- each manufacturer row shows `product_count = 30`

### Backup Database
```bash
cp data.db data.db.backup
```

### Reset Database
```bash
rm data.db
# Then re-initialize: db.create_all() or schema.sql
```

---

## 8. Troubleshooting

### Issue: "No module named flask"
**Solution:**
```bash
source venv/bin/activate
pip install flask flask-sqlalchemy flask-cors
```

### Issue: "Address already in use" (port 5000)
**Solution:**
```bash
# Find process using port 5000
lsof -i :5000

# Kill it
kill -9 <PID>

# Or use different port in app.py: app.run(debug=True, port=5001)
```

### Issue: React page not reachable on `http://127.0.0.1:5173/`
**Why it happens:**
- Vite defaults to port 5173, but if that port is occupied it automatically moves to the next available port (commonly 5174).

**Solution:**
```bash
cd /Users/nicky/Projects/OnesToManys/frontend-react
npm run dev
```

Then open the exact Local URL printed by Vite, for example:
- `http://localhost:5174/`

If you specifically want 5173, free it first:
```bash
lsof -nP -iTCP:5173 -sTCP:LISTEN
kill -9 <PID>
```

### Issue: Tests fail with "No module named app"
**Solution:**
```bash
# Make sure you're in project root
cd /Users/nicky/Projects/OnesToManys
source venv/bin/activate
pytest tests/ -v
```

### Issue: Database locked error
**Solution:**
```bash
# Close Flask server (Ctrl+C)
# Delete data.db
rm data.db
# Restart Flask to recreate fresh database
```

### Issue: "Missing required fields" when creating product
**Why it happens:**
- You are posting to `/api/products` or `/api/manufacturers/{id}/products` with an incomplete JSON body.
- This is not caused by missing seed data.

**Minimum working flow:**
```bash
# 1) Create a manufacturer first
curl -X POST http://127.0.0.1:5000/api/manufacturers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "TestMaker",
    "country": "USA",
    "founded_year": 2000,
    "headquarters_city": "Austin"
  }'

# 2) Create product using nested route (no manufacturer_id field required in body)
curl -X POST http://127.0.0.1:5000/api/manufacturers/1/products \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Widget",
    "category": "Demo",
    "price": 19.99,
    "stock_quantity": 5
  }'
```

**If you use `/api/products` instead of nested route:**
- Include all required fields: `manufacturer_id`, `product_name`, `category`, `price`, `stock_quantity`.

### Issue: terminal shows `quote>` after paste
**Why it happens:**
- Your shell saw an opening quote `'` or `"` without a matching closing quote.
- This usually happens when multiline curl JSON was pasted with a missing trailing `'`.

**How to exit `quote>` mode:**
- Press `Ctrl+C` to cancel the unfinished command.

**Use one-line commands to avoid this:**
```bash
curl -X POST http://127.0.0.1:5000/api/manufacturers -H "Content-Type: application/json" -d '{"name":"TestMaker","country":"USA","founded_year":2000,"headquarters_city":"Austin"}'
curl -X POST http://127.0.0.1:5000/api/manufacturers/1/products -H "Content-Type: application/json" -d '{"product_name":"Widget","category":"Demo","price":19.99,"stock_quantity":5}'
```

### Issue: Python file gets accidental pasted corruption (example: `app.py` export block)
**Why it happens:**
- A clipboard paste or editor glitch can inject non-Python fragments into a dict/list block.
- In this project, `_export_payload()` is especially sensitive because one malformed line breaks app startup.

**How to detect quickly:**
```bash
cd /Users/nicky/Projects/OnesToManys
python -m py_compile app.py
```

If this fails, inspect around:
- `def _export_payload()`
- `def _load_payload(payload)`

**Known-good shape in `_export_payload()`:**
```python
return {
  "manufacturers": [
    {
      **manufacturer.to_dict(),
      "products": [
        product.to_dict()
        for product in sorted(manufacturer.products, key=lambda item: item.product_id)
      ],
    }
    for manufacturer in manufacturers
  ]
}
```

### Issue: `rg` command not found while searching files
**Why it happens:**
- `ripgrep` is not installed or not available on PATH in the current terminal.

**Fallback options:**
```bash
# Filename/path discovery
find . -type f | grep "frontend-vanilla"

# Text search with line numbers
grep -Rin "manufacturerProductTable" frontend-vanilla
```

### Issue: CORS errors in browser
**Solution:**
Flask app has CORS enabled. If issues persist:
```python
# In app.py, verify:
from flask_cors import CORS
CORS(app)
```

---

## 9. Project Structure Reminder

**Files You Created/Modified:**
```
app.py                    - Flask API (11 endpoints)
models.py                 - SQLAlchemy ORM (Manufacturer, Product)
schema.sql                - Database DDL (optional, if using SQL approach)
seed_data.sql             - Test data (optional)
data.db                   - SQLite database (auto-created)
tests/
  conftest.py             - Pytest fixtures
  unit/test_models.py     - 8 unit tests
  integration/test_manufacturers_api.py  - 10+ integration tests
  integration/test_products_api.py       - 15+ integration tests
references/
  app_annotated_cp.py
  models_annotated_cp.py
  test_*_annotated_cp.py  - Teaching copies
TESTING_GUIDE.md          - How to run tests
PHASE1_ARCHITECTURE.md    - Complete architecture
CLAUDE.md                 - Behavioral guidelines
PROJECT_PLAN.md           - 3-phase plan
```

---

## 10. Next Steps After Phase 1 Validation

1. ✅ **Verify all 40+ tests pass**: `pytest tests/ -v`
2. ✅ **Manual API testing**: Use curl commands above
3. ✅ **Cascade delete verification**: Follow section 6
4. ✅ **Database inspection**: Use sqlite3 commands

Then proceed to **Phase 2**:
- Implement nested relationship endpoints
- Add import/export (JSON and SQL)
- Create comprehensive integration tests for Phase 2 features

---

## 11. Common Commands (Reference)

```bash
# Activate environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run Flask server
python3 app.py

# Run single test
pytest tests/unit/test_models.py::TestManufacturerModel::test_should_create_manufacturer_with_valid_data -v

# Check database
sqlite3 data.db ".tables"

# Stop Flask (in Flask terminal)
Ctrl+C

# Deactivate venv
deactivate

# Fresh database
rm data.db  # Delete
python3 app.py  # Restart Flask to recreate
```

---

## Success Checklist

- [ ] Venv activated
- [ ] Dependencies installed
- [ ] Database created (data.db exists)
- [ ] All 40+ tests pass
- [ ] Flask server starts on port 5000
- [ ] Can create manufacturer via curl
- [ ] Can create product linked to manufacturer
- [ ] Cascade delete works (delete mfg, products disappear)
- [ ] All error cases handled (400, 404, 409)
- [ ] Database queries work (sqlite3 commands)

✅ **Phase 1 Complete and Validated!**
