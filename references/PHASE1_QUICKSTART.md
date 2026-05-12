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

Important guardrail:
- If you see fixture errors from files in `references/`, verify `pytest.ini` includes:
  - `testpaths = tests`
  - `norecursedirs = references`

### 5. Start Flask Backend Server
```bash
/Users/nicky/Projects/OnesToManys/venv/bin/python app.py
```

Expected server log lines:
- `* Serving Flask app 'app'`
- `* Debug mode: on`
- `* Running on http://127.0.0.1:5000`

### 6. Verify API Health and Core Endpoints (Second Terminal)
```bash
curl http://127.0.0.1:5000/
curl http://127.0.0.1:5000/api/manufacturers
curl http://127.0.0.1:5000/api/products
```

Expected health response:
- `{"message":"Manufacturer-Products API is running"}`

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
