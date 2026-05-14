-- seed_data.sql
-- Purpose: Populate manufacturers and products with synthetic data for testing.
-- Relationship target: 12 manufacturers, 30 products each (360 total products).
-- Added sales stats so the UI can visualize revenue, units sold, and origin patterns.

PRAGMA foreign_keys = ON;

-- Clear existing data for consistent seed behavior.
DELETE FROM products;
DELETE FROM manufacturers;

INSERT INTO manufacturers (
    manufacturer_id,
    name,
    country,
    founded_year,
    headquarters_city,
    is_active
) VALUES
    (1, 'Sony', 'Japan', 1946, 'Tokyo', 1),
    (2, 'Samsung Electronics', 'South Korea', 1969, 'Suwon', 1),
    (3, 'Apple', 'United States', 1976, 'Cupertino', 1),
    (4, 'Bosch', 'Germany', 1886, 'Stuttgart', 1),
    (5, 'Philips', 'Netherlands', 1891, 'Amsterdam', 1),
    (6, 'Panasonic', 'Japan', 1918, 'Kadoma', 1),
    (7, 'Dell Technologies', 'United States', 1984, 'Round Rock', 1),
    (8, 'Lenovo', 'China', 1984, 'Beijing', 1),
    (9, 'Whirlpool', 'United States', 1911, 'Benton Harbor', 1),
    (10, 'Nokia', 'Finland', 1865, 'Espoo', 1),
    (11, 'LG Electronics', 'South Korea', 1958, 'Seoul', 1),
    (12, 'Honeywell', 'United States', 1906, 'Charlotte', 1);

-- Generate exactly 30 products per manufacturer to make one-to-many relationships
-- obvious in UI lists, SQL joins, and API responses.
WITH RECURSIVE product_numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1
    FROM product_numbers
    WHERE n < 30
)
,
seeded_products AS (
    SELECT
        m.manufacturer_id,
        m.name || ' Model ' || printf('%02d', pn.n) AS product_name,
        CASE (pn.n % 6)
            WHEN 0 THEN 'Smartphone'
            WHEN 1 THEN 'Laptop'
            WHEN 2 THEN 'Home Appliance'
            WHEN 3 THEN 'Audio'
            WHEN 4 THEN 'Networking'
            ELSE 'Accessory'
        END AS category,
        ROUND(
            (119.0 + (pn.n * 12.75))
            * CASE m.manufacturer_id
                WHEN 1 THEN 1.10
                WHEN 2 THEN 1.18
                WHEN 3 THEN 1.42
                WHEN 4 THEN 1.02
                WHEN 5 THEN 0.98
                WHEN 6 THEN 1.05
                WHEN 7 THEN 1.16
                WHEN 8 THEN 1.08
                WHEN 9 THEN 0.94
                WHEN 10 THEN 0.90
                WHEN 11 THEN 1.00
                ELSE 1.24
            END
            * CASE (pn.n % 6)
                WHEN 0 THEN 1.30
                WHEN 1 THEN 1.55
                WHEN 2 THEN 1.10
                WHEN 3 THEN 1.00
                WHEN 4 THEN 1.20
                ELSE 0.72
            END
            * (1 + (((pn.n % 5) - 2) * 0.035))
            , 2
        ) AS price,
        CAST(
            35
            + ((m.manufacturer_id * 17 + pn.n * 19) % 240)
            * CASE (pn.n % 6)
                WHEN 0 THEN 0.95
                WHEN 1 THEN 0.85
                WHEN 2 THEN 1.10
                WHEN 3 THEN 1.20
                WHEN 4 THEN 0.92
                ELSE 1.35
            END
            AS INTEGER
        ) AS stock_quantity,
        MAX(
            8,
            CAST(
                (
                    28 + ((m.manufacturer_id * 11 + pn.n * 23) % 210)
                )
                * CASE m.manufacturer_id
                    WHEN 1 THEN 1.10
                    WHEN 2 THEN 1.25
                    WHEN 3 THEN 1.35
                    WHEN 4 THEN 0.86
                    WHEN 5 THEN 0.91
                    WHEN 6 THEN 1.02
                    WHEN 7 THEN 1.18
                    WHEN 8 THEN 1.12
                    WHEN 9 THEN 0.78
                    WHEN 10 THEN 0.73
                    WHEN 11 THEN 0.97
                    ELSE 1.28
                END
                * CASE (pn.n % 6)
                    WHEN 0 THEN 1.28
                    WHEN 1 THEN 1.14
                    WHEN 2 THEN 0.94
                    WHEN 3 THEN 1.00
                    WHEN 4 THEN 1.06
                    ELSE 0.72
                END
                * CASE ((m.manufacturer_id * 9 + pn.n * 5) % 10)
                    WHEN 0 THEN 1.08
                    WHEN 1 THEN 1.08
                    WHEN 2 THEN 1.08
                    WHEN 3 THEN 1.08
                    WHEN 4 THEN 1.00
                    WHEN 5 THEN 1.00
                    WHEN 6 THEN 1.00
                    WHEN 7 THEN 1.22
                    WHEN 8 THEN 1.22
                    ELSE 0.84
                END
                * CASE ((m.manufacturer_id * 7 + pn.n * 3) % 20)
                    WHEN 0 THEN 1.14
                    WHEN 1 THEN 1.14
                    WHEN 2 THEN 1.14
                    WHEN 3 THEN 1.14
                    WHEN 4 THEN 1.14
                    WHEN 5 THEN 1.00
                    WHEN 6 THEN 1.00
                    WHEN 7 THEN 1.00
                    WHEN 8 THEN 1.00
                    WHEN 9 THEN 1.20
                    WHEN 10 THEN 1.20
                    WHEN 11 THEN 1.20
                    WHEN 12 THEN 1.20
                    WHEN 13 THEN 1.20
                    WHEN 14 THEN 1.20
                    WHEN 15 THEN 0.86
                    WHEN 16 THEN 0.86
                    WHEN 17 THEN 0.90
                    WHEN 18 THEN 0.90
                    ELSE 0.90
                END
                * (1 + (((pn.n % 6) - 3) * 0.05))
                AS INTEGER
            )
        ) AS units_sold,
        CASE ((m.manufacturer_id * 7 + pn.n * 3) % 20)
            WHEN 0 THEN 'North America'
            WHEN 1 THEN 'North America'
            WHEN 2 THEN 'North America'
            WHEN 3 THEN 'North America'
            WHEN 4 THEN 'North America'
            WHEN 5 THEN 'Europe'
            WHEN 6 THEN 'Europe'
            WHEN 7 THEN 'Europe'
            WHEN 8 THEN 'Europe'
            WHEN 9 THEN 'Asia Pacific'
            WHEN 10 THEN 'Asia Pacific'
            WHEN 11 THEN 'Asia Pacific'
            WHEN 12 THEN 'Asia Pacific'
            WHEN 13 THEN 'Asia Pacific'
            WHEN 14 THEN 'Asia Pacific'
            WHEN 15 THEN 'South America'
            WHEN 16 THEN 'South America'
            WHEN 17 THEN 'Middle East & Africa'
            WHEN 18 THEN 'Middle East & Africa'
            ELSE 'Middle East & Africa'
        END AS order_origin,
        CASE ((m.manufacturer_id * 9 + pn.n * 5) % 10)
            WHEN 0 THEN 'Online'
            WHEN 1 THEN 'Online'
            WHEN 2 THEN 'Online'
            WHEN 3 THEN 'Online'
            WHEN 4 THEN 'Retail'
            WHEN 5 THEN 'Retail'
            WHEN 6 THEN 'Retail'
            WHEN 7 THEN 'Direct'
            WHEN 8 THEN 'Direct'
            ELSE 'Distributor'
        END AS sales_channel,
        'Synthetic seed product ' || printf('%02d', pn.n) || ' for ' || m.name || ' (manufacturer_id=' || m.manufacturer_id || ').'
            AS description
    FROM manufacturers AS m
    CROSS JOIN product_numbers AS pn
)
INSERT INTO products (
    manufacturer_id,
    product_name,
    category,
    price,
    stock_quantity,
    units_sold,
    revenue,
    order_origin,
    sales_channel,
    description
)
SELECT
    s.manufacturer_id,
    s.product_name,
    s.category,
    s.price,
    s.stock_quantity,
    s.units_sold,
    ROUND((s.price * s.units_sold), 2) AS revenue,
    s.order_origin,
    s.sales_channel,
    s.description
FROM seeded_products AS s;
