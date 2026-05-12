# Testing Infrastructure Guide

## Overview

Phase 1 includes **40+ comprehensive tests** covering:
- **Unit tests** (8): ORM model behavior, constraints, relationships
- **Integration tests** (30+): HTTP endpoints, validation, cascade delete

All tests follow **AAA Pattern** (Arrange-Act-Assert) and use pytest fixtures for reusability.

---

## Running Tests

Environment setup is maintained in [PHASE1_QUICKSTART.md](PHASE1_QUICKSTART.md).
For exact backend recreation commands (venv, installs, pytest, server start, curl checks), use:
- `Backend Manual Recreation (Canonical Command Log)` in [PHASE1_QUICKSTART.md](PHASE1_QUICKSTART.md).

Current test layout:
```
tests/
├── __init__.py
├── conftest.py
├── unit/
│   └── test_models.py
└── integration/
    ├── test_manufacturers_api.py
    └── test_products_api.py
```

### Execute All Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v

# Run single test class
pytest tests/integration/test_manufacturers_api.py::TestManufacturerPostEndpoint -v

# Run single test
pytest tests/integration/test_manufacturers_api.py::TestManufacturerPostEndpoint::test_should_create_manufacturer_with_valid_data -v
```

### Expected Output

Successful run shows:
```
tests/unit/test_models.py::TestManufacturerModel::test_should_create_manufacturer_with_valid_data PASSED
tests/unit/test_models.py::TestManufacturerModel::test_should_serialize_manufacturer_to_dict PASSED
...
======================== 40 passed in 0.42s ========================
```

---

## Test Organization

### Unit Tests (tests/unit/test_models.py)

Tests ORM models **in isolation** from HTTP layer.

**TestManufacturerModel (5 tests):**
- `test_should_create_manufacturer_with_valid_data`: Field assignment works
- `test_should_serialize_manufacturer_to_dict`: to_dict() returns all fields
- `test_should_enforce_unique_manufacturer_name`: Unique constraint enforced
- `test_should_have_empty_products_list_initially`: Relationship initialized empty
- `test_should_update_manufacturer_timestamps`: Audit trail works (created_at immutable, updated_at changes)

**TestProductModel (7 tests):**
- `test_should_create_product_with_valid_data`: Field assignment works
- `test_should_serialize_product_to_dict`: to_dict() returns all fields including Decimal→float conversion
- `test_should_link_product_to_manufacturer`: FK relationship navigable
- `test_should_enforce_unique_product_name_per_manufacturer`: Composite unique constraint works
- `test_should_allow_same_product_name_different_manufacturer`: Uniqueness scoped to manufacturer
- `test_should_update_product_timestamps`: Audit trail works
- Implicit: Decimal precision verified in to_dict() conversion

### Integration Tests

Tests HTTP endpoints, validation, error handling, and relationships.

**test_manufacturers_api.py:**

*TestManufacturerGetEndpoints (4 tests)*
- Empty list handling
- List all manufacturers
- Get single by ID
- 404 not found

*TestManufacturerPostEndpoint (5 tests)*
- Create valid manufacturer
- Validation: missing required field (400)
- Constraint: duplicate name (409)
- Optional: is_active parameter

*TestManufacturerPutEndpoint (3 tests)*
- Partial update
- 404 not found
- Constraint: cannot rename to duplicate (409)

*TestManufacturerDeleteEndpoint (2 tests)*
- Delete existing
- 404 not found

**test_products_api.py:**

*TestProductGetEndpoints (4 tests)*
- Empty list handling
- List all products
- Get single by ID
- 404 not found

*TestProductPostEndpoint (7 tests)*
- Create valid product
- Validation: missing required field (400)
- FK validation: manufacturer not found (404)
- Validation: negative price (400)
- Validation: negative stock (400)
- Constraint: duplicate name per manufacturer (409)
- Boundary: same name allowed in different manufacturer (201)

*TestProductPutEndpoint (3 tests)*
- Partial update
- 404 not found
- Validation: negative price rejected (400)

*TestProductDeleteEndpoint (2 tests)*
- Delete existing
- 404 not found

*TestProductManufacturerRelationship (2 tests)*
- **Cascade delete**: Deleting manufacturer deletes all its products
- **FK constraint**: Invalid manufacturer_id rejected (404)

---

## Test Scenarios Covered

### ✅ Positive Scenarios
- Valid CRUD operations (create, read, update, delete)
- Serialization to JSON
- Timestamps (created_at, updated_at)
- Optional fields (is_active, description)
- Relationship navigation

### ✅ Negative Scenarios
- Missing required fields (400)
- Invalid manufacturer reference (404)
- Negative prices/stock (400)
- Duplicate names (409, with context)

### ✅ Boundary Conditions
- Empty database (GET returns [])
- Non-existent resources (404)
- Unique constraint scoped to manufacturer (same name OK elsewhere)
- Max/min decimal precision (Decimal → float)

### ✅ Relationship Integrity
- Cascade delete: manufacturer deletion removes products
- FK constraint: product must link to real manufacturer
- Composite unique: (manufacturer_id, product_name)

---

## Test Fixtures (conftest.py)

Shared fixtures eliminate boilerplate:

```python
@pytest.fixture
def client():
    """Fresh Flask test client with in-memory DB per test."""
    # Sets up app with :memory: SQLite
    # Runs db.create_all()
    # Yields client, then cleans up

@pytest.fixture
def sample_manufacturer(client):
    """Creates TestCorp manufacturer in fresh DB."""
    # Creates: name="TestCorp", country="USA", founded_year=2020
    # Yields the object with auto-generated manufacturer_id

@pytest.fixture
def sample_product(client, sample_manufacturer):
    """Creates TestProduct linked to sample_manufacturer."""
    # Creates: product_name="TestProduct", manufacturer_id=sample_mfg.id
    # Yields the object with auto-generated product_id
```

Each test gets a **fresh database** for isolation.

---

## Debugging a Failed Test

If a test fails:

1. **Read the assertion error** - pytest shows exactly which assertion failed
2. **Check the test docstring** - WHY/ACT/ASSERT explains intent
3. **Run only that test** for faster iteration:
   ```bash
   pytest tests/integration/test_products_api.py::TestProductPostEndpoint::test_should_return_400_when_price_is_negative -v
   ```
4. **Check annotated copy** in `references/` folder for detailed explanations
5. **Trace the code path** - usually in `app.py` error handling or `models.py` constraints

---

## Common Test Patterns

### Pattern 1: Positive Case (Should Succeed)
```python
def test_should_create_manufacturer_with_valid_data(self, client):
    payload = {"name": "NewCorp", ...}
    response = client.post("/api/manufacturers", json=payload)
    
    assert response.status_code == 201  # Success!
    assert response.json["manufacturer_id"] is not None
```

### Pattern 2: Validation (Should Fail with 400)
```python
def test_should_return_400_when_missing_required_field(self, client):
    payload = {...}  # Missing 'name'
    response = client.post("/api/manufacturers", json=payload)
    
    assert response.status_code == 400  # Validation failed
    assert "error" in response.json
```

### Pattern 3: Constraint (Should Fail with 409)
```python
def test_should_return_409_when_name_already_exists(self, client, sample_manufacturer):
    payload = {"name": "TestCorp"}  # Duplicate!
    response = client.post("/api/manufacturers", json=payload)
    
    assert response.status_code == 409  # Conflict (unique violation)
```

### Pattern 4: Not Found (Should Fail with 404)
```python
def test_should_return_404_when_manufacturer_not_found(self, client):
    response = client.get("/api/manufacturers/999")  # Doesn't exist
    
    assert response.status_code == 404
```

### Pattern 5: Relationship (Cascade Behavior)
```python
def test_should_cascade_delete_products(self, client, sample_product, sample_manufacturer):
    # Delete manufacturer
    client.delete(f"/api/manufacturers/{mfg_id}")
    
    # Verify product also deleted
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 404  # Cascaded!
```

---

## Phase 3 Manual Recreation (Command Log)

This section is a reproducible command record for recreating the React Phase 3 baseline manually.

### 1. Backend Validation Before Frontend Work

```bash
cd /Users/nicky/Projects/OnesToManys
/Users/nicky/Projects/OnesToManys/venv/bin/python -m pytest
```

Expected result:
- `54 passed`
- Warning-only output is acceptable (`LegacyAPIWarning` from SQLAlchemy Query.get)

Important note:
- If you accidentally run pytest without test scoping and see many fixture errors from `references/`, ensure `pytest.ini` has:
    - `testpaths = tests`
    - `norecursedirs = references`

### 2. Scaffold React App (Interactive Input Required)

```bash
cd /Users/nicky/Projects/OnesToManys
npm create vite@latest frontend-react -- --template react
```

Required terminal input during scaffold:
- Prompt: `Ok to proceed? (y)`
    - Input: `y`
- Prompt: `Install with npm and start now?`
    - Input: choose `No` (manual control of commands)

If scaffold is partially created and you rerun command:
- Message: `Target directory "frontend-react" is not empty`
- Action: cancel operation and continue with existing generated folder.

### 3. Install and Validate Frontend Build

```bash
cd /Users/nicky/Projects/OnesToManys/frontend-react
npm install
npm run build
```

Expected result:
- Vite build completes successfully
- Output includes `built in ...ms`

### 4. Run Full Stack Locally

Terminal A (backend):

```bash
cd /Users/nicky/Projects/OnesToManys
/Users/nicky/Projects/OnesToManys/venv/bin/python app.py
```

Terminal B (frontend):

```bash
cd /Users/nicky/Projects/OnesToManys/frontend-react
npm run dev
```

### 5. Files Created/Updated For Phase 3 React Baseline

Production frontend files:
- `frontend-react/src/App.jsx`
- `frontend-react/src/App.css`
- `frontend-react/src/index.css`
- `frontend-react/src/components/ManufacturerList.jsx`
- `frontend-react/src/components/ManufacturerDetail.jsx`
- `frontend-react/src/components/ProductList.jsx`
- `frontend-react/src/services/api.js`

Annotated learning references:
- `references/frontend-react/src/App_annotated_cp.jsx`
- `references/frontend-react/src/App_annotated_cp.css`
- `references/frontend-react/src/index_annotated_cp.css`
- `references/frontend-react/src/main_annotated_cp.jsx`
- `references/frontend-react/src/components/ManufacturerList_annotated_cp.jsx`
- `references/frontend-react/src/components/ManufacturerDetail_annotated_cp.jsx`
- `references/frontend-react/src/components/ProductList_annotated_cp.jsx`
- `references/frontend-react/src/services/api_annotated_cp.js`

---

## Key Testing Principles (from CLAUDE.md § 7)

1. **AAA Pattern**: Every test clearly shows Arrange → Act → Assert
2. **One Thing Only**: Each test covers one specific behavior
3. **Descriptive Naming**: `test_should_*` format explains intent
4. **Independent**: Tests run in any order, in isolation
5. **Fast & Reliable**: No flaky tests; use fixtures for state
6. **Treat as Production**: Clean, maintainable test code

---

## Next Steps

1. **Run tests**: `pytest tests/ -v` ✅
2. **Verify all pass** ✅
3. **Phase 2**: Add relationship endpoints (GET /api/manufacturers/{id}/products, etc.)
4. **Phase 2**: Add import/export (JSON and SQL)
5. **Phase 3**: Build frontends (Vanilla JS, React)

---

## Document Scope

This guide is intentionally test-focused.

For environment setup and API manual checks, use:
- [PHASE1_QUICKSTART.md](PHASE1_QUICKSTART.md)
