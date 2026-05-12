-- schema.sql
-- Purpose: Create the Manufacturer (master) and Product (detail) tables
-- for the OnesToManys project using a one-to-many relationship.

PRAGMA foreign_keys = ON;

-- Drop detail first to avoid foreign key dependency conflicts during re-runs.
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS manufacturers;

CREATE TABLE manufacturers (
    manufacturer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    country TEXT NOT NULL,
    founded_year INTEGER NOT NULL,
    headquarters_city TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    CHECK (founded_year BETWEEN 1800 AND 2100),
    CHECK (is_active IN (0, 1))
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    manufacturer_id INTEGER NOT NULL,
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
    CHECK (price >= 0),
    CHECK (stock_quantity >= 0),
    UNIQUE (manufacturer_id, product_name)
);

-- Indexes to speed up relationship lookups and common filters.
CREATE INDEX idx_products_manufacturer_id ON products (manufacturer_id);
CREATE INDEX idx_products_category ON products (category);
CREATE INDEX idx_manufacturers_country ON manufacturers (country);
