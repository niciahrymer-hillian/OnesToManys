# Phase 1 Architecture Summary

## Purpose
This document captures Phase 1 system design decisions only.

Operational setup/run steps live in:
- [PHASE1_QUICKSTART.md](PHASE1_QUICKSTART.md)

Testing execution and patterns live in:
- [TESTING_GUIDE.md](TESTING_GUIDE.md)

## System Overview
Phase 1 implements a 3-tier Manufacturer-Products service:
- Data layer: SQLite
- Domain layer: SQLAlchemy models
- API layer: Flask REST endpoints

Core domain shape:
- Manufacturer (master)
- Product (detail)
- Cardinality: one manufacturer to many products

## Technology Stack
| Layer | Technology |
|---|---|
| Database | SQLite |
| ORM | SQLAlchemy (Flask-SQLAlchemy) |
| API Framework | Flask |
| Cross-Origin | flask-cors |
| Testing | pytest |

## Data Model Decisions

### Manufacturer
- Primary key: `manufacturer_id`
- Unique business key: `name`
- Lifecycle fields: `created_at`, `updated_at`
- Relationship: owns many products

### Product
- Primary key: `product_id`
- Foreign key: `manufacturer_id` -> `manufacturers.manufacturer_id`
- Composite uniqueness: `(manufacturer_id, product_name)`
- Lifecycle fields: `created_at`, `updated_at`
- Price stored with decimal precision

### Integrity Constraints
- FK constraint on product -> manufacturer
- Cascade delete at relationship boundary
- Uniqueness constraints to prevent duplicate manufacturer names and per-manufacturer product name collisions

## API Surface

### Manufacturers
- `GET /api/manufacturers`
- `POST /api/manufacturers`
- `GET /api/manufacturers/{id}`
- `PUT /api/manufacturers/{id}`
- `DELETE /api/manufacturers/{id}`

### Products
- `GET /api/products`
- `POST /api/products`
- `GET /api/products/{id}`
- `PUT /api/products/{id}`
- `DELETE /api/products/{id}`

### Health
- `GET /`

## Validation and Error Model
- Request validation at API boundary
- Business checks before persistence (e.g., FK existence)
- Constraint enforcement at DB level as final guard

Expected response classes:
- `200`: successful reads/updates/deletes
- `201`: successful creates
- `400`: invalid input or business validation failure
- `404`: missing resource or missing referenced manufacturer
- `409`: uniqueness conflict

## Architectural Tradeoffs
- SQLite chosen for Phase 1 simplicity and speed of setup
- Explicit master-detail modeling keeps domain intent clear
- Annotated reference copies improve onboarding and design traceability

## Phase 2 Architectural Extensions
- Nested relationship endpoints under manufacturer scope
- Import/export flows (JSON/SQL)
- Additional integration coverage for relationship routes and round-trip data integrity
