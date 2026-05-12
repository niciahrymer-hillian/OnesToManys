# OnesToManys Project Plan: Manufacturer (Master) - Products (Detail)

## Project Overview

Build a 3-tier web application that manages Manufacturers and their Products using a master-detail relationship. The application will have a REST API backend, SQL database, and web frontend for CRUD operations.

---

## Phase 1: Foundation & Core API (Days 1-2)

**Phase Objective**: Establish a working database schema and REST API that supports basic CRUD operations on both Manufacturer and Product entities independently.

### Day 1: Planning & Database Schema

**Objective**: Design and document the data model and create SQL files that will form the foundation for all future development. These will be used to initialize the database.

#### Tasks:
- [ ] Define data model for Manufacturer and Product entities
- [ ] Design database schema with normalized tables
- [ ] Document entity relationships and constraints
- [ ] Create SQL schema file (`schema.sql`)
- [ ] Create SQL file with synthetic generated data (`seed_data.sql`)

#### Data Model:

**Manufacturer (Master)**
- manufacturer_id (PK)
- name (string, unique)
- country (string)
- founded_year (integer)
- headquarters_city (string)
- is_active (boolean)

**Product (Detail)**
- product_id (PK)
- manufacturer_id (FK to Manufacturer)
- product_name (string)
- category (string)
- price (decimal)
- stock_quantity (integer)
- description (text)
- created_at (timestamp)

#### Constraints:
- Manufacturer.manufacturer_id is unique primary key
- Product.manufacturer_id must reference existing Manufacturer
- Delete cascade: removing a Manufacturer deletes its Products
- Product requires a valid Manufacturer

### Day 2: REST API - CRUD Operations

**Objective**: Implement a working REST API with full CRUD functionality on both entities. This establishes the backend layer that the frontend will communicate with.

#### Backend Setup:
- [ ] Initialize project structure (Python/Java framework choice)
- [ ] Set up database connection
- [ ] Create data access layer (models/entities)

#### API Endpoints - Phase 1:

**Why These Endpoints**: These 10 endpoints (5 per entity) provide complete CRUD coverage. They allow the frontend to create, retrieve, update, and delete both manufacturers and products.

**Manufacturer CRUD**
- `GET /api/manufacturers` - List all manufacturers
- `POST /api/manufacturers` - Create new manufacturer
- `GET /api/manufacturers/{id}` - Get manufacturer details
- `PUT /api/manufacturers/{id}` - Update manufacturer
- `DELETE /api/manufacturers/{id}` - Delete manufacturer

**Product CRUD**
- `GET /api/products` - List all products
- `POST /api/products` - Create new product
- `GET /api/products/{id}` - Get product details
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

#### Testing (curl):

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

**Phase Objective**: Build the relationship layer that allows clients to query and manage products through their manufacturer. Add data persistence so the database can be exported and imported.

### Day 3: One-to-Many Relationship Endpoints

**Objective**: Create nested REST endpoints that expose the manufacturer-product relationship. This enables clients to work with products in the context of a specific manufacturer.

#### New API Endpoints:

**Why Nested Endpoints**: Instead of querying all products and filtering client-side, `/api/manufacturers/{id}/products` gives the server the context to efficiently return only the manufacturer's products. This is more RESTful and performant.

**Manufacturer-Product Relationship**
- `GET /api/manufacturers/{id}/products` - Get all products for a manufacturer
- `POST /api/manufacturers/{id}/products` - Create product for specific manufacturer
- `GET /api/manufacturers/{id}/products/{productId}` - Get specific product of manufacturer
- `PUT /api/manufacturers/{id}/products/{productId}` - Update product of manufacturer
- `DELETE /api/manufacturers/{id}/products/{productId}` - Delete product of manufacturer

#### Response Examples:

```json
GET /api/manufacturers/1
{
  "manufacturer_id": 1,
  "name": "Sony",
  "country": "Japan",
  "founded_year": 1946,
  "headquarters_city": "Tokyo",
  "is_active": true
}

GET /api/manufacturers/1/products
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

**Objective**: Implement data import/export capabilities and perform comprehensive testing of all Phase 2 endpoints using a visual REST client. This ensures data can be backed up, shared, and reloaded.

#### Tasks:

**Why These Tasks**:
- Export/import capabilities ensure data persistence and allow testing scenarios to be easily reset
- GUI client testing validates the relationship endpoints work correctly and have proper response formats

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

**Phase Objective**: Create two complete user interfaces that allow non-technical users to interact with the API through web browsers. Both frontends will implement the same functionality using different approaches.

### Day 5-6: Vanilla JavaScript Frontend

**Objective**: Build a fully functional UI without using any JavaScript framework. This demonstrates core web concepts and creates a working interface using only HTML, CSS, and vanilla JS.

#### Pages to Build:

**Why These Pages**: Together they provide complete CRUD functionality for manufacturers and products, plus relationship navigation.
- [ ] Dashboard page (view all manufacturers)
- [ ] Manufacturer detail page (view manufacturer + all products)
- [ ] Product list page (all products)
- [ ] Create manufacturer form
- [ ] Edit manufacturer form
- [ ] Create product form (with manufacturer selection)
- [ ] Edit product form
- [ ] Delete confirmation modals

#### Features:
- Dynamic product listing under each manufacturer
- Search/filter by manufacturer name
- Search/filter products by category
- Real-time form validation
- Success/error notifications

### Day 7: React Frontend

**Objective**: Rebuild the same UI using React to demonstrate component-based architecture, reusability, and state management. This provides a modern comparison to the vanilla JS approach.

#### Components to Build:

**Why Component-Based**: Breaking the UI into reusable React components makes the code more maintainable and demonstrates how to structure larger applications.
- [ ] `<ManufacturerList />` - List all manufacturers
- [ ] `<ManufacturerDetail />` - Show manufacturer with products
- [ ] `<ManufacturerForm />` - Create/edit manufacturer
- [ ] `<ProductList />` - List all products
- [ ] `<ProductForm />` - Create/edit product (with manufacturer picker)
- [ ] `<ProductCard />` - Reusable product display
- [ ] `<Navigation />` - Main navigation
- [ ] State management (Context API or Redux for sharing data)

#### Features:
- [ ] List manufacturers with product counts
- [ ] View all products for a manufacturer
- [ ] Add/edit/delete manufacturers
- [ ] Add/edit/delete products
- [ ] Filter products by manufacturer
- [ ] Display manufacturer details alongside products
- [ ] Handle loading and error states

---

## Technical Stack Decision

Choose one of the following stacks:

### Option A: Python + Flask/FastAPI
- Backend: Flask or FastAPI
- Database: SQLite3 or PostgreSQL
- Frontend: Vanilla JS + React

### Option B: Java + Spring Boot
- Backend: Spring Boot + Spring Data REST
- Database: PostgreSQL or MySQL
- Frontend: Vanilla JS + React

---

## Deliverables Checklist

**How to Know When Each Phase is Complete**: Use this checklist to verify all objectives have been achieved.

### Phase 1: Completed When...
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
- [ ] One-to-many relationship endpoints
  - **Objective Achieved**: Clients can work with products through manufacturer context
- [ ] Data import/export (JSON and SQL)
  - **Objective Achieved**: Data can be backed up and restored
- [ ] Tested with GUI REST client (Postman/Insomnia)
  - **Objective Achieved**: All relationship endpoints visually verified
- [ ] All CRUD operations on relationships functional
  - **Objective Achieved**: All nested resource operations work correctly

### Phase 3: Completed When...
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

- **Data Integrity**: Manufacturer deletion should cascade to Products
- **API Versioning**: Consider `/api/v1/` prefix for future scalability
- **Pagination**: For Phase 2+, consider adding pagination to list endpoints
- **Validation**: Implement input validation for all form submissions
- **Error Handling**: Consistent error response format across all endpoints
- **Documentation**: Keep API documentation updated as endpoints are added
