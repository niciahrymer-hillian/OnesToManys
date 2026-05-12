# OnesToManys Project Plan: Manufacturer (Master) - Products (Detail)
<!-- [DOCUMENT_PURPOSE]: Comprehensive project plan for 3-phase development of a Master-Detail application -->
<!-- [GUIDELINE_SOURCE]: Based on README.md phase structure and OnesToManys project guidelines -->

## Project Overview
<!-- [SECTION_PURPOSE]: Establish the project scope and define what we're building -->
<!-- [DOMAIN]: Manufacturer-Products master-detail relationship -->

Build a 3-tier web application that manages Manufacturers and their Products using a master-detail relationship. The application will have a REST API backend, SQL database, and web frontend for CRUD operations.

---

## Phase 1: Foundation & Core API (Days 1-2)
<!-- [PHASE_PURPOSE]: Establish database schema and basic CRUD operations for both entities -->
<!-- [PHASE_OUTCOME]: Working REST API with full CRUD on master and detail tables -->
<!-- [OBJECTIVE]: Establish a working database schema and REST API that supports basic CRUD operations on both Manufacturer and Product entities independently -->

**Phase Objective**: Establish a working database schema and REST API that supports basic CRUD operations on both Manufacturer and Product entities independently.

### Day 1: Planning & Database Schema
<!-- [DAY_PURPOSE]: Design data model and create SQL files for initialization -->
<!-- [OBJECTIVE]: Design and document the data model and create SQL files that will form the foundation for all future development -->

**Objective**: Design and document the data model and create SQL files that will form the foundation for all future development. These will be used to initialize the database.

#### Tasks:
<!-- [TASK_SECTION]: Activities to achieve the day 1 objective -->

- [ ] Define data model for Manufacturer and Product entities
  - **Achieves**: Clear understanding of what data we'll store
- [ ] Design database schema with normalized tables
  - **Achieves**: Optimized table structure without redundancy
- [ ] Document entity relationships and constraints
  - **Achieves**: Enforcement of data integrity rules (foreign keys, cascade)
- [ ] Create SQL schema file (`schema.sql`)
  - **Achieves**: Reproducible database creation
- [ ] Create SQL file with synthetic generated data (`seed_data.sql`)
  - **Achieves**: Test data for development and validation

#### Data Model:
<!-- [DATA_MODEL_SECTION]: Defines the structure of entities and their fields -->

**Manufacturer (Master)**
<!-- [ENTITY]: Master entity - independent, primary information container -->
<!-- [FIELD_DEFINITIONS]: All attributes that describe a Manufacturer -->
- manufacturer_id (PK)
  <!-- [PRIMARY_KEY]: Unique identifier for each manufacturer -->
- name (string, unique)
  <!-- [CONSTRAINT]: Name must be unique across all manufacturers -->
- country (string)
  <!-- [FIELD]: Geographic information for manufacturer location -->
- founded_year (integer)
  <!-- [FIELD]: Historical information about company -->
- headquarters_city (string)
  <!-- [FIELD]: Specific location information -->
- is_active (boolean)
  <!-- [FIELD]: Business status flag for filtering/operations -->

**Product (Detail)**
<!-- [ENTITY]: Detail entity - dependent on Manufacturer, cannot exist alone -->
<!-- [FIELD_DEFINITIONS]: All attributes that describe a Product -->
- product_id (PK)
  <!-- [PRIMARY_KEY]: Unique identifier for each product -->
- manufacturer_id (FK to Manufacturer)
  <!-- [FOREIGN_KEY]: Links Product to its owning Manufacturer -->
  <!-- [RELATIONSHIP]: Many products belong to one manufacturer -->
- product_name (string)
  <!-- [FIELD]: Product identification -->
- category (string)
  <!-- [FIELD]: Classification for filtering/searching -->
- price (decimal)
  <!-- [FIELD]: Monetary value of product -->
- stock_quantity (integer)
  <!-- [FIELD]: Inventory tracking -->
- description (text)
  <!-- [FIELD]: Extended product information -->
- created_at (timestamp)
  <!-- [FIELD]: Audit trail for when product was added -->

#### Constraints:
<!-- [CONSTRAINTS_SECTION]: Database integrity rules that enforce the master-detail relationship -->
- Manufacturer.manufacturer_id is unique primary key
  <!-- [CONSTRAINT_PURPOSE]: Ensures each manufacturer has one unique identity -->
- Product.manufacturer_id must reference existing Manufacturer
  <!-- [CONSTRAINT_PURPOSE]: Referential integrity - prevents orphaned products -->
- Delete cascade: removing a Manufacturer deletes its Products
  <!-- [CONSTRAINT_PURPOSE]: Cleanup rule - no products without manufacturer -->
- Product requires a valid Manufacturer
  <!-- [CONSTRAINT_PURPOSE]: Enforces that products are always related to a manufacturer -->

### Day 2: REST API - CRUD Operations
<!-- [DAY_PURPOSE]: Implement basic CRUD endpoints for both entities without relationships -->
<!-- [OBJECTIVE]: Implement a working REST API with full CRUD functionality on both entities -->

**Objective**: Implement a working REST API with full CRUD functionality on both entities. This establishes the backend layer that the frontend will communicate with.

#### Backend Setup:
<!-- [SETUP_SECTION]: Infrastructure tasks to enable API implementation -->
- [ ] Initialize project structure (Python/Java framework choice)
  - **Achieves**: Project organized with proper directories and config
- [ ] Set up database connection
  - **Achieves**: Backend can communicate with database
- [ ] Create data access layer (models/entities)
  - **Achieves**: Object-relational mapping between code and database

#### API Endpoints - Phase 1:
<!-- [ENDPOINT_DESIGN]: Basic CRUD operations on entities -->
<!-- [API_PHILOSOPHY]: RESTful design with standard HTTP methods -->
<!-- [OBJECTIVE_LINK]: These 10 endpoints (5 per entity) provide complete CRUD coverage -->

**Why These Endpoints**: These 10 endpoints (5 per entity) provide complete CRUD coverage. They allow the frontend to create, retrieve, update, and delete both manufacturers and products.

**Manufacturer CRUD**
<!-- [RESOURCE]: /api/manufacturers - primary resource endpoint -->
- `GET /api/manufacturers` - List all manufacturers
  <!-- [OPERATION]: Read all - no filtering in Phase 1 -->
- `POST /api/manufacturers` - Create new manufacturer
  <!-- [OPERATION]: Create with request body -->
- `GET /api/manufacturers/{id}` - Get manufacturer details
  <!-- [OPERATION]: Read one - specific resource by ID -->
- `PUT /api/manufacturers/{id}` - Update manufacturer
  <!-- [OPERATION]: Update - replace entire resource -->
- `DELETE /api/manufacturers/{id}` - Delete manufacturer
  <!-- [OPERATION]: Delete - remove resource (no cascade yet) -->

**Product CRUD**
<!-- [RESOURCE]: /api/products - primary resource endpoint -->
- `GET /api/products` - List all products
  <!-- [OPERATION]: Read all products -->
- `POST /api/products` - Create new product
  <!-- [OPERATION]: Create with manufacturer_id in body -->
- `GET /api/products/{id}` - Get product details
  <!-- [OPERATION]: Read one specific product -->
- `PUT /api/products/{id}` - Update product
  <!-- [OPERATION]: Update product attributes -->
- `DELETE /api/products/{id}` - Delete product
  <!-- [OPERATION]: Remove product -->

#### Testing (curl):
<!-- [TESTING_PHASE]: Manual validation of endpoints before moving to Phase 2 -->
<!-- [OBJECTIVE]: Validate that each endpoint works correctly before moving to Phase 2 -->

**Why Test These**: Manual testing with curl validates that each endpoint works correctly before moving to Phase 2. This prevents broken APIs from being used in relationship endpoints.

- [ ] Test GET /api/manufacturers
  - **Goal**: Verify we can retrieve all manufacturers
- [ ] Test GET /api/products
  - **Goal**: Verify we can retrieve all products
- [ ] Test POST operations for both
  - **Goal**: Verify we can create new records
- [ ] Verify data integrity
  - **Goal**: Confirm foreign key constraints are enforced

---

## Phase 2: Relationship Integration & Advanced Operations (Days 3-4)
<!-- [PHASE_PURPOSE]: Implement one-to-many relationship endpoints and data persistence -->
<!-- [PHASE_OUTCOME]: Full relationship CRUD and import/export functionality -->
<!-- [OBJECTIVE]: Build the relationship layer and data persistence capabilities -->

**Phase Objective**: Build the relationship layer that allows clients to query and manage products through their manufacturer. Add data persistence so the database can be exported and imported.

### Day 3: One-to-Many Relationship Endpoints
<!-- [DAY_PURPOSE]: Add nested resource endpoints for manufacturer-product relationships -->
<!-- [OBJECTIVE]: Expose the manufacturer-product relationship through REST endpoints -->

**Objective**: Create nested REST endpoints that expose the manufacturer-product relationship. This enables clients to work with products in the context of a specific manufacturer.

#### New API Endpoints:
<!-- [ENDPOINT_DESIGN]: Hierarchical URLs reflecting master-detail relationship -->
<!-- [API_PHILOSOPHY]: RESTful nested resources - /masters/{masterId}/details -->
<!-- [OBJECTIVE_LINK]: Nested endpoints enable efficient relationship queries -->

**Why Nested Endpoints**: Instead of querying all products and filtering client-side, `/api/manufacturers/{id}/products` gives the server the context to efficiently return only the manufacturer's products. This is more RESTful and performant.

**Manufacturer-Product Relationship**
<!-- [RESOURCE_HIERARCHY]: Products nested under Manufacturers -->
- `GET /api/manufacturers/{id}/products` - Get all products for a manufacturer
  <!-- [OPERATION]: Read all details for specific master -->
  <!-- [EFFECT]: Returns only products linked to this manufacturer -->
- `POST /api/manufacturers/{id}/products` - Create product for specific manufacturer
  <!-- [OPERATION]: Create detail linked to specific master -->
  <!-- [EFFECT]: Automatically sets manufacturer_id on new product -->
- `GET /api/manufacturers/{id}/products/{productId}` - Get specific product of manufacturer
  <!-- [OPERATION]: Read one detail of specific master -->
  <!-- [EFFECT]: Verifies product belongs to manufacturer -->
- `PUT /api/manufacturers/{id}/products/{productId}` - Update product of manufacturer
  <!-- [OPERATION]: Update detail within master context -->
  <!-- [EFFECT]: May include moving to different manufacturer -->
- `DELETE /api/manufacturers/{id}/products/{productId}` - Delete product of manufacturer
  <!-- [OPERATION]: Delete detail from master -->
  <!-- [EFFECT]: Removes relationship and product record -->

#### Response Examples:
<!-- [RESPONSE_FORMAT]: JSON structure showing actual API contract -->

```json
GET /api/manufacturers/1
<!-- [RESPONSE_TYPE]: Single Manufacturer resource -->
<!-- [CONTAINS]: Master entity with all attributes -->
{
  "manufacturer_id": 1,
  "name": "Sony",
  "country": "Japan",
  "founded_year": 1946,
  "headquarters_city": "Tokyo",
  "is_active": true
}

GET /api/manufacturers/1/products
<!-- [RESPONSE_TYPE]: Array of Product resources -->
<!-- [CONTAINS]: All products related to manufacturer 1 -->
<!-- [RELATIONSHIP_SHOWN]: Each product has manufacturer_id reference -->
[
  {
    "product_id": 101,
    "manufacturer_id": 1,
    "product_name": "PlayStation 5",
    "category": "Gaming Console",
    "price": 499.99,
    "stock_quantity": 150,
    "description": "Next-gen gaming console"
  },
  {
    "product_id": 102,
    "manufacturer_id": 1,
    "product_name": "WH-1000XM5 Headphones",
    "category": "Audio",
    "price": 399.99,
    "stock_quantity": 300
  }
]
```

### Day 4: Data Persistence & REST Client Testing
<!-- [DAY_PURPOSE]: Add import/export and validate all operations via GUI client -->
<!-- [OBJECTIVE]: Enable data persistence and comprehensive relationship testing -->

**Objective**: Implement data import/export capabilities and perform comprehensive testing of all Phase 2 endpoints using a visual REST client. This ensures data can be backed up, shared, and reloaded.

#### Tasks:
<!-- [TASK_SECTION]: Activities to achieve the day 4 objective -->
<!-- [OBJECTIVE_LINK]: These tasks provide data persistence and comprehensive validation -->

**Why These Tasks**: Export/import capabilities ensure data persistence and allow testing scenarios to be easily reset. GUI client testing validates the relationship endpoints work correctly and have proper response formats.

- [ ] Implement data dump functionality (SQL export)
  - **Achieves**: Ability to backup entire database as SQL
- [ ] Implement data load functionality (SQL import)
  - **Achieves**: Ability to restore database from backup
- [ ] Implement JSON export functionality
  - **Achieves**: Ability to share data with frontend and external systems
- [ ] Implement JSON import functionality
  - **Achieves**: Ability to load test data from JSON files
- [ ] Test all endpoints using Postman/Insomnia
  - **Achieves**: Verification that all relationship endpoints work correctly

#### Test Scenarios:
<!-- [TEST_COVERAGE]: Comprehensive scenarios covering all relationships -->
<!-- [OBJECTIVE_LINK]: Each scenario tests a different relationship aspect -->

**Why These Scenarios**: Each tests a different aspect of the master-detail relationship to ensure data integrity and correct cascade behavior.

- [ ] Create manufacturer and multiple products
  - **Tests**: Foreign key creation and relationship linking
- [ ] Query manufacturer with all related products
  - **Tests**: Nested endpoint returns correct filtered results
- [ ] Update product and verify relationship integrity
  - **Tests**: Updates don't break foreign key references
- [ ] Delete product and verify orphan handling
  - **Tests**: Deleting detail doesn't affect master
- [ ] Delete manufacturer and verify cascade delete
  - **Tests**: Cascade rule removes all related products
- [ ] Export data to JSON and re-import
  - **Tests**: Data persistence and round-trip integrity

---

## Phase 3: User Interfaces (Days 5-7)
<!-- [PHASE_PURPOSE]: Create web interfaces for end users to interact with the API -->
<!-- [PHASE_OUTCOME]: Two complete frontends (Vanilla JS and React) with CRUD UI -->
<!-- [OBJECTIVE]: Create working user interfaces for both technical and modern approaches -->

**Phase Objective**: Create two complete user interfaces that allow non-technical users to interact with the API through web browsers. Both frontends will implement the same functionality using different approaches.

### Day 5-6: Vanilla JavaScript Frontend
<!-- [DAY_PURPOSE]: Build functional UI without framework for core functionality -->
<!-- [TECHNOLOGY]: Pure JavaScript, HTML, CSS - no build tools -->
<!-- [OBJECTIVE]: Create a working UI without frameworks to demonstrate core web concepts -->

**Objective**: Build a fully functional UI without using any JavaScript framework. This demonstrates core web concepts and creates a working interface using only HTML, CSS, and vanilla JS.

#### Pages to Build:
<!-- [PAGE_LIST]: All URLs and pages needed for complete CRUD interface -->
<!-- [OBJECTIVE_LINK]: Together these pages provide complete CRUD functionality -->

**Why These Pages**: Together they provide complete CRUD functionality for manufacturers and products, plus relationship navigation.
- [ ] Dashboard page (view all manufacturers)
  <!-- [PURPOSE]: Landing page showing all manufacturers with counts -->
- [ ] Manufacturer detail page (view manufacturer + all products)
  <!-- [PURPOSE]: Show master entity with all related details -->
- [ ] Product list page (all products)
  <!-- [PURPOSE]: View all products globally (not filtered by manufacturer) -->
- [ ] Create manufacturer form
  <!-- [PURPOSE]: UI for POST /api/manufacturers -->
- [ ] Edit manufacturer form
  <!-- [PURPOSE]: UI for PUT /api/manufacturers/{id} -->
- [ ] Create product form (with manufacturer selection)
  <!-- [PURPOSE]: UI for POST /api/products with manufacturer picker -->
- [ ] Edit product form
  <!-- [PURPOSE]: UI for PUT /api/products/{id} -->
- [ ] Delete confirmation modals
  <!-- [PURPOSE]: Confirmation dialogs for destructive operations -->

#### Features:
<!-- [FEATURE_REQUIREMENTS]: UI/UX functionality expectations -->
- Dynamic product listing under each manufacturer
  <!-- [UX_FEATURE]: Show products grouped by manufacturer -->
- Search/filter by manufacturer name
  <!-- [UX_FEATURE]: Allow user to find manufacturers quickly -->
- Search/filter products by category
  <!-- [UX_FEATURE]: Allow product filtering by category -->
- Real-time form validation
  <!-- [UX_FEATURE]: Show validation errors before submission -->
- Success/error notifications
  <!-- [UX_FEATURE]: User feedback on operation results -->

### Day 7: React Frontend
<!-- [DAY_PURPOSE]: Build same functionality using React framework for reusability -->
<!-- [TECHNOLOGY]: React with hooks, Component-based architecture -->
<!-- [OBJECTIVE]: Rebuild UI using React to demonstrate modern component-based approach -->

**Objective**: Rebuild the same UI using React to demonstrate component-based architecture, reusability, and state management. This provides a modern comparison to the vanilla JS approach.

#### Components to Build:
<!-- [COMPONENT_LIST]: Reusable React components for the application -->
<!-- [OBJECTIVE_LINK]: Component-based architecture enables reusability and maintainability -->

**Why Component-Based**: Breaking the UI into reusable React components makes the code more maintainable and demonstrates how to structure larger applications.
- [ ] `<ManufacturerList />` - List all manufacturers
  <!-- [COMPONENT_PURPOSE]: Display list of master entities -->
  <!-- [PROPS]: manufacturers array -->
- [ ] `<ManufacturerDetail />` - Show manufacturer with products
  <!-- [COMPONENT_PURPOSE]: Detail view of master with nested details -->
  <!-- [PROPS]: manufacturerId, products array -->
- [ ] `<ManufacturerForm />` - Create/edit manufacturer
  <!-- [COMPONENT_PURPOSE]: Form for create/update master -->
  <!-- [PROPS]: manufacturerId (optional for edit mode) -->
- [ ] `<ProductList />` - List all products
  <!-- [COMPONENT_PURPOSE]: Display all detail entities -->
  <!-- [PROPS]: products array -->
- [ ] `<ProductForm />` - Create/edit product (with manufacturer picker)
  <!-- [COMPONENT_PURPOSE]: Form for create/update detail -->
  <!-- [PROPS]: productId (optional), manufacturerId (optional), manufacturers array -->
- [ ] `<ProductCard />` - Reusable product display
  <!-- [COMPONENT_PURPOSE]: Single product display unit -->
  <!-- [PROPS]: product object -->
- [ ] `<Navigation />` - Main navigation
  <!-- [COMPONENT_PURPOSE]: Links between pages -->
  <!-- [PROPS]: current page state -->
- [ ] State management (Context API or Redux for sharing data)
  <!-- [ARCHITECTURE]: Centralized state for manufacturer/product data -->

#### Features:
<!-- [FEATURE_REQUIREMENTS]: React-specific functionality -->
- [ ] List manufacturers with product counts
  <!-- [UX_FEATURE]: Show how many products each manufacturer has -->
- [ ] View all products for a manufacturer
  <!-- [UX_FEATURE]: Click manufacturer to see related products -->
- [ ] Add/edit/delete manufacturers
  <!-- [UX_FEATURE]: Full CRUD on master entities -->
- [ ] Add/edit/delete products
  <!-- [UX_FEATURE]: Full CRUD on detail entities -->
- [ ] Filter products by manufacturer
  <!-- [UX_FEATURE]: Subset products to one manufacturer -->
- [ ] Display manufacturer details alongside products
  <!-- [UX_FEATURE]: Show relationship context -->
- [ ] Handle loading and error states
  <!-- [UX_FEATURE]: Show loading spinners and error messages -->

---

## Technical Stack Decision
<!-- [DECISION_POINT]: Choose one stack for the entire project -->

Choose one of the following stacks:

### Option A: Python + Flask/FastAPI
<!-- [STACK_OPTION]: Python-based backend -->
- Backend: Flask or FastAPI
  <!-- [CHOICE]: FastAPI recommended for easier REST, Flask for simplicity -->
- Database: SQLite3 or PostgreSQL
  <!-- [CHOICE]: SQLite3 for Phase 1-2 simplicity, PostgreSQL for Phase 3+ scale -->
- Frontend: Vanilla JS + React
  <!-- [CHOICE]: Same frontend for both stacks -->

### Option B: Java + Spring Boot
<!-- [STACK_OPTION]: Java-based backend -->
- Backend: Spring Boot + Spring Data REST
  <!-- [CHOICE]: Enterprise framework with built-in relationship support -->
- Database: PostgreSQL or MySQL
  <!-- [CHOICE]: Industry standard databases -->
- Frontend: Vanilla JS + React
  <!-- [CHOICE]: Same frontend for both stacks -->

---

## Deliverables Checklist
<!-- [CHECKLIST_PURPOSE]: Verify completion of all requirements per phase -->
<!-- [OBJECTIVE_LINK]: Use this to verify all objectives have been achieved -->

**How to Know When Each Phase is Complete**: Use this checklist to verify all objectives have been achieved.

### Phase 1: Completed When...
<!-- [PHASE_DELIVERABLES]: Minimum viable schema and API -->
- [ ] `schema.sql` - Database schema
  - **Objective Achieved**: Data model is documented and can be recreated
- [ ] `seed_data.sql` - Synthetic test data
  - **Objective Achieved**: Test data is available for all testing
- [ ] Runnable REST API server
  - **Objective Achieved**: Backend is running and accepting requests
- [ ] All CRUD endpoints functional
  - **Objective Achieved**: Both entities have complete create/read/update/delete
- [ ] Tested with curl
  - **Objective Achieved**: All endpoints verified to work correctly

### Phase 2: Completed When...
<!-- [PHASE_DELIVERABLES]: Relationship operations and data persistence -->
- [ ] One-to-many relationship endpoints
  - **Objective Achieved**: Clients can work with products through manufacturer context
- [ ] Data import/export (JSON and SQL)
  - **Objective Achieved**: Data can be backed up and restored
- [ ] Tested with GUI REST client (Postman/Insomnia)
  - **Objective Achieved**: All relationship endpoints visually verified
- [ ] All CRUD operations on relationships functional
  - **Objective Achieved**: All nested resource operations work correctly

### Phase 3: Completed When...
<!-- [PHASE_DELIVERABLES]: Complete user interfaces -->
- [ ] Vanilla JS frontend (functional)
  - **Objective Achieved**: Users can interact with API without technical tools
- [ ] React frontend (functional)
  - **Objective Achieved**: Modern component-based version works
- [ ] All CRUD operations via UI
  - **Objective Achieved**: No need to use curl or Postman anymore
- [ ] Dynamic manufacturer-product display
  - **Objective Achieved**: Master-detail relationship is visible and usable
- [ ] Form validation and error handling
  - **Objective Achieved**: Users get clear feedback on success/failure

---

## Notes & Considerations
<!-- [NOTES_SECTION]: Design principles and best practices for implementation -->

- **Data Integrity**: Manufacturer deletion should cascade to Products
  <!-- [WHY]: Prevent orphaned products (detail without master) -->
  <!-- [IMPLEMENTATION]: Database cascade rule + API validation -->

- **API Versioning**: Consider `/api/v1/` prefix for future scalability
  <!-- [WHY]: Allow future API versions without breaking existing clients -->
  <!-- [IMPLEMENTATION]: Add version prefix to all endpoints -->

- **Pagination**: For Phase 2+, consider adding pagination to list endpoints
  <!-- [WHY]: Handle large datasets efficiently -->
  <!-- [IMPLEMENTATION]: Limit/offset parameters on GET list endpoints -->

- **Validation**: Implement input validation for all form submissions
  <!-- [WHY]: Prevent invalid data from entering database -->
  <!-- [IMPLEMENTATION]: Backend validation + frontend validation -->

- **Error Handling**: Consistent error response format across all endpoints
  <!-- [WHY]: Predictable errors for frontend error handling -->
  <!-- [IMPLEMENTATION]: Standard error response schema with status codes -->

- **Documentation**: Keep API documentation updated as endpoints are added
  <!-- [WHY]: Enable team members and future clients to use API correctly -->
  <!-- [IMPLEMENTATION]: Docstrings, Swagger/OpenAPI, or README updates -->
