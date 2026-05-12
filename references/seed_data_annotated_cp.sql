-- [FILE] seed_data_annotated_cp.sql
-- [PURPOSE] Insert synthetic master/detail test data.
-- [WHY] Enables immediate API and query testing in Phase 1.
-- [EFFECT] Provides realistic relationship records for curl and UI tests.

PRAGMA foreign_keys = ON;
-- [CONFIG] Ensures FK rules are active while loading data.

-- [RESET] Clear detail first, then master, to satisfy FK dependencies.
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
    (10, 'Nokia', 'Finland', 1865, 'Espoo', 1);
-- [DATASET][MASTER] 10 manufacturers across regions for diverse filtering.

INSERT INTO products (
    product_id,
    manufacturer_id,
    product_name,
    category,
    price,
    stock_quantity,
    description
) VALUES
    (1001, 1, 'PlayStation 5', 'Gaming Console', 499.99, 120, 'Current generation home gaming console.'),
    (1002, 1, 'WH-1000XM5', 'Headphones', 399.99, 260, 'Noise-canceling over-ear headphones.'),
    (1003, 2, 'Galaxy S25', 'Smartphone', 999.99, 190, 'Flagship Android smartphone.'),
    (1004, 2, 'Galaxy Tab S10', 'Tablet', 749.99, 145, 'Premium Android tablet.'),
    (1005, 3, 'iPhone 17', 'Smartphone', 1099.99, 210, 'Latest iPhone model.'),
    (1006, 3, 'MacBook Pro 14', 'Laptop', 1999.99, 85, 'Professional laptop for creators and developers.'),
    (1007, 4, 'Series 8 Drill', 'Power Tool', 229.99, 75, 'Cordless drill for home and workshop use.'),
    (1008, 4, 'Smart Thermostat X', 'Home Automation', 179.99, 130, 'Programmable thermostat with app control.'),
    (1009, 5, 'Hue Starter Kit', 'Lighting', 199.99, 165, 'Smart LED lighting starter bundle.'),
    (1010, 5, 'Airfryer XXL', 'Kitchen Appliance', 249.99, 90, 'High-capacity digital air fryer.'),
    (1011, 6, 'Lumix G9 II', 'Camera', 1699.99, 40, 'Mirrorless camera for photography and video.'),
    (1012, 6, 'NN-SN686S', 'Microwave', 189.99, 105, 'Countertop microwave oven.'),
    (1013, 7, 'XPS 13', 'Laptop', 1299.99, 95, 'Ultrabook for business and student use.'),
    (1014, 7, 'UltraSharp 27', 'Monitor', 499.99, 140, '27-inch professional IPS monitor.'),
    (1015, 8, 'ThinkPad X1 Carbon', 'Laptop', 1499.99, 70, 'Business-class lightweight laptop.'),
    (1016, 8, 'Legion Pro 7', 'Gaming Laptop', 2199.99, 35, 'High-performance gaming notebook.'),
    (1017, 9, 'Top Load Washer 5.3', 'Laundry Appliance', 899.99, 60, 'High-efficiency top load washing machine.'),
    (1018, 9, 'French Door Refrigerator 26', 'Refrigerator', 2299.99, 28, 'Large-capacity smart refrigerator.'),
    (1019, 10, 'XR21 Router', 'Networking', 129.99, 180, 'Dual-band home Wi-Fi router.'),
    (1020, 10, 'Beacon Mesh 2-Pack', 'Networking', 199.99, 125, 'Mesh Wi-Fi system for whole-home coverage.');
-- [DATASET][DETAIL] 20 products (2 each) to validate one-to-many relationships.
