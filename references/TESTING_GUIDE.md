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

Manual black-box API verification is also available with curl:

```bash
chmod +x scripts/phase2_curl_checks.sh
./scripts/phase2_curl_checks.sh
```

This complements pytest by exercising the running server from outside the Flask test client.

### Using curl As Phase 2 Evidence

If you are using curl instead of a GUI REST client, keep the evidence explicit in your submission notes:

1. Start the Flask server locally.
2. Run `./scripts/phase2_curl_checks.sh` and save the terminal output.
3. If needed, include the individual curl commands for nested routes plus `/api/export/json` and `/api/import/json`.
4. State clearly that curl was used to validate the endpoints from a running server.

Important limitation:
- This satisfies the API testing intent.
- It does not satisfy the README's GUI-client wording if that requirement is enforced literally.

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

## Phase 3 Manual UI Checklist (Pass/Fail)

Use this checklist when validating the React UI manually against the running backend.

### Setup

1. Start backend server:
    - `cd /Users/nicky/Projects/OnesToManys`
    - `source venv/bin/activate`
    - `python app.py`
2. Start frontend dev server in a second terminal:
    - `cd /Users/nicky/Projects/OnesToManys/frontend-react`
    - `npm run dev`
3. Open the Vite URL shown in terminal.
   - Important: if 5173 is occupied, Vite auto-switches ports (for example to 5174). Use the exact `Local` URL printed by Vite.
   - Example fallback URL: `http://localhost:5174/`

### Manufacturer CRUD

1. **Create manufacturer**
    - Fill Add Manufacturer form in list panel.
    - Click Add Manufacturer.
    - Pass criteria: New manufacturer appears in list and can be selected.

2. **Read manufacturer details**
    - Select the newly created manufacturer.
    - Pass criteria: Detail panel shows name, location, founded year, and status.

3. **Update manufacturer**
    - In Edit Manufacturer section, change one or more fields.
    - Click Save Manufacturer.
    - Pass criteria: Updated values remain after reselecting the manufacturer.

4. **Delete manufacturer**
    - Click Delete Manufacturer and confirm.
    - Pass criteria: Manufacturer disappears from list.

### Product CRUD (Nested Under Selected Manufacturer)

1. **Create product**
    - Select a manufacturer.
    - Fill product form and click Add Product.
    - Pass criteria: Product appears in product table for that manufacturer.

2. **Read product list**
    - Stay on selected manufacturer.
    - Pass criteria: Product table shows product name, category, price, and stock.

3. **Update product**
    - Click Edit on a product row.
    - Change one or more fields and click Update Product.
    - Pass criteria: Product row reflects new values.

4. **Delete product**
    - Click Delete on a product row.
    - Pass criteria: Product row is removed from table.

### Relationship Integrity

1. Create one manufacturer with two products.
2. Select a different manufacturer.
3. Pass criteria: Product table changes by selected manufacturer scope only.

### Optional API Cross-Check

After UI actions, confirm backend state:

- `curl http://127.0.0.1:5000/api/manufacturers`
- `curl http://127.0.0.1:5000/api/products`
- `curl http://127.0.0.1:5000/api/manufacturers/<manufacturer_id>/products`

Pass criteria: API output matches what UI shows.

---

## Phase 3 Vanilla UI Manual Run (Pancake Menu)

Use this when validating the Vanilla JavaScript implementation.

### Start Servers

1. Backend API:
    - `cd /Users/nicky/Projects/OnesToManys`
    - `source venv/bin/activate`
    - `python app.py`
2. Static server for Vanilla frontend (new terminal):
    - `cd /Users/nicky/Projects/OnesToManys/frontend-vanilla`
    - `python3 -m http.server 8080`
3. Open:
    - `http://127.0.0.1:8080/index.html`

### Pancake Menu Navigation Check

1. Click the pancake menu button (`≡`) on Home.
2. Navigate to Manufacturers page.
3. Open menu again and navigate to Products page.
4. Repeat from Products back to Home.

Pass criteria:
- Menu opens/closes on every page.
- All pages are reachable from the menu.
- Active page link is highlighted.

### Vanilla CRUD + Search Check

1. On Manufacturers page:
    - Create manufacturer.
    - Search list by name/country/city.
    - Edit and delete selected manufacturer.
2. On Products page:
    - Select manufacturer context.
    - Create, edit, and delete products.
    - Search products by name/category/description.

Pass criteria:
- UI actions reflect immediately in lists/tables.
- Errors are shown inline for invalid operations.
- Product actions remain scoped to selected manufacturer.

---

## Frontend Merge Timing (React + Vanilla)

Recommended point to merge:
- After both frontends pass one manual checklist run (React checklist and Vanilla checklist) on the same backend.

Why this point:
- It locks functional parity first, so merge work is structural and lower risk.

Prerequisites before merge:
1. React build passes (`npm run build` in `frontend-react`).
2. Vanilla scripts pass syntax checks.
3. Manual CRUD + search checks pass in both UIs.

Suggested merge sequence:
1. Create a single launcher page that links to both UIs (soft merge).
2. Decide target long-term UI (`React` or `Vanilla`) as canonical.
3. Port any missing behavior from non-canonical UI to canonical UI.
4. Keep one UI as archive/demo or retire it after parity confirmation.

Notes:
- There is no automatic merge of the two frontends.
- They already share one backend API, which is the stable integration point.

### Soft-Merge Launcher (Implemented)

Launcher file:
- `/Users/nicky/Projects/OnesToManys/frontend-launcher/index.html`

How to run launcher:
1. Start backend API (`python app.py`).
2. Start React dev server (`npm run dev` in `frontend-react`).
3. Start Vanilla static server (`python3 -m http.server 8080` in `frontend-vanilla`).
4. Serve launcher page from project root:
    - `cd /Users/nicky/Projects/OnesToManys`
    - `python3 -m http.server 8090`
5. Open `http://127.0.0.1:8090/frontend-launcher/index.html`.

Pass criteria:
- Launcher opens.
- React link opens React UI.
- Vanilla links open the corresponding Vanilla pages.

---

## React-Canonical Consolidation Plan

This plan follows the selected strategy:
- Short-term: keep soft-merge launcher while validating both UIs.
- Medium-term: make React the canonical frontend.
- Long-term: keep Vanilla as archived learning/demo reference.

### Phase A: Finish Validation (Now)

1. Run one full React manual checklist pass.
2. Run one full Vanilla manual checklist pass.
3. Record any parity gaps between React and Vanilla behavior.

Exit criteria:
- Both UIs pass CRUD + search checks against same backend state.
- Any remaining gap is documented and prioritized.

### Phase B: Lock React As Canonical

1. Treat `frontend-react/` as the only actively developed UI.
2. Route all future feature requests and bug fixes to React first.
3. Keep launcher page, but mark React as primary path.

Exit criteria:
- New work is implemented only in React.
- Team notes/docs call out React as canonical.

### Phase C: Archive Vanilla (No Active Development)

1. Freeze `frontend-vanilla/` as read-only reference/demo.
2. Keep it runnable for demos with static server commands.
3. Stop parity updates unless explicitly required by assignment/demo.

Exit criteria:
- Vanilla remains functional for demo use.
- No new features are required to be backported.

### Phase D: Optional Final Merge Cleanup

1. Keep launcher as unified entry (recommended for demos).
2. Optionally add archive notice banner in Vanilla pages.
3. Optionally add a single README section for launch commands.

Exit criteria:
- Single starting point exists for all stakeholders.
- Canonical path and archive path are unambiguous.

---

## Definition Of Done (Final Merge State)

The consolidation is considered complete when all items below are true:

1. React is the canonical UI and receives all ongoing changes.
2. Vanilla is explicitly marked archive/demo-only.
3. Launcher page is available and links to both modes.
4. Backend API compatibility is verified with React flows.
5. Manual test checklist passes for React.
6. Reference docs reflect the canonical/archive split.
7. Annotated references are up to date for changed files.

Optional but recommended:
- Add a dated "Consolidation Decision" note in references for traceability.

---

## Consolidation Decision Record

Date: 2026-05-13

Decision:
- React is the canonical frontend for active development.
- Vanilla JS is retained as archive/demo and learning reference.
- Soft-merge launcher remains the single entry page to both modes.

Rationale:
1. React provides stronger maintainability for ongoing feature growth.
2. Vanilla remains valuable as instructional/reference material without doubling active feature work.
3. Launcher preserves usability for demos and transition periods.

Impact:
1. New frontend features and fixes are implemented in React first.
2. Vanilla updates are limited to archive health/demo needs.
3. Documentation and test checklists reflect canonical/archive split.

Review trigger:
- Revisit this decision only if assignment requirements or team constraints explicitly require dual active frontends.

---

## Final Review Snapshot (2026-05-13)

Validation summary:
1. Backend tests: 57 passed.
2. React frontend build: passed.
3. Vanilla script syntax checks: passed.

Quick API demo executed:
1. Created manufacturer (`DemoMfg`) via `POST /api/manufacturers`.
2. Created nested product (`DemoWidget`) via `POST /api/manufacturers/1/products`.
3. Verified one-to-many list via `GET /api/manufacturers/1/products`.
4. Exported JSON via `GET /api/export/json`.
5. Re-imported JSON via `POST /api/import/json`.

Observed result:
- Demo endpoints returned expected payloads and status behavior during run.
- Repaired accidental corruption in `app.py` inside `_export_payload()` and verified syntax with `python -m py_compile app.py`.

### Post-Edit Safety Check Learned During Implementation

When editing backend import/export logic in `app.py`, run a syntax guard before restarting servers:

```bash
cd /Users/nicky/Projects/OnesToManys
python -m py_compile app.py
```

Why this is now required in practice:
1. `_export_payload()` and `_load_payload()` are dense nested structures.
2. A single accidental pasted fragment can invalidate the file.
3. `py_compile` catches this immediately without waiting for runtime route calls.

Optional follow-up smoke checks after compile passes:

```bash
curl http://127.0.0.1:5000/api/export/json
curl -X POST http://127.0.0.1:5000/api/import/json \
    -H "Content-Type: application/json" \
    --data-binary @export.json
```

---

## Document Scope

This guide is intentionally test-focused.

For environment setup and API manual checks, use:
- [PHASE1_QUICKSTART.md](PHASE1_QUICKSTART.md)
