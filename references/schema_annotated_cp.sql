-- [FILE] schema_annotated_cp.sql
-- [PURPOSE] Create normalized master-detail tables for Manufacturer -> Products.
-- [WHY] Establishes enforceable data integrity before API development.
-- [EFFECT] Day 1 objective: a reproducible relational schema with constraints.

PRAGMA foreign_keys = ON;
-- [CONFIG] Enables foreign key enforcement in SQLite sessions.

-- [ORDERING] Drop detail first because it depends on master.
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS manufacturers;

CREATE TABLE manufacturers (
    manufacturer_id INTEGER PRIMARY KEY,
    -- [FIELD][PK] Unique master identifier.

    name TEXT NOT NULL UNIQUE,
    -- [FIELD] Human-readable manufacturer name.
    -- [CONSTRAINT] UNIQUE prevents duplicate manufacturer names.

    country TEXT NOT NULL,
    founded_year INTEGER NOT NULL,
    headquarters_city TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    -- [FIELD] Stored as 0/1 for SQLite boolean compatibility.

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    -- [FIELD] Basic auditing timestamps.

    CHECK (founded_year BETWEEN 1800 AND 2100),
    -- [CONSTRAINT] Prevents unrealistic year values.

    CHECK (is_active IN (0, 1))
    -- [CONSTRAINT] Restricts active status to boolean-like values.
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    -- [FIELD][PK] Unique detail identifier.

    manufacturer_id INTEGER NOT NULL,
    -- [FIELD][FK] Links product to its parent manufacturer.

    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    description TEXT,

    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (manufacturer_id)
        REFERENCES manufacturers (manufacturer_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    -- [RELATIONSHIP] One manufacturer -> many products.
    -- [CONSTRAINT] Cascade delete keeps referential integrity.

    CHECK (price >= 0),
    CHECK (stock_quantity >= 0),
    -- [CONSTRAINT] Prevents invalid business values.

    UNIQUE (manufacturer_id, product_name)
    -- [CONSTRAINT] Avoids duplicate product names per manufacturer.
);

-- [INDEX] Speeds up manufacturer -> products lookups.
CREATE INDEX idx_products_manufacturer_id ON products (manufacturer_id);

-- [INDEX] Helps filtering/browsing products by category.
CREATE INDEX idx_products_category ON products (category);

-- [INDEX] Helps optional country-based manufacturer filtering.
CREATE INDEX idx_manufacturers_country ON manufacturers (country);
