USE smart_sales_db;

-- Sample regions
INSERT INTO regions (name) VALUES ('North'), ('South'), ('East'), ('West'), ('Central');

-- Sample customers (IDs match CSV-style IDs like CUST0001)
INSERT INTO customers (customer_id, customer_name, region_id) VALUES
('CUST0001', 'Alice Johnson', 1),
('CUST0002', 'Bob Smith', 2),
('CUST0003', 'Carol Lee', 3),
('CUST0004', 'David Brown', 4),
('CUST0005', 'Eva Green', 5);

-- Sample products
INSERT INTO products (product_name, category, unit_price) VALUES
('UltraPhone X','Electronics',699.00),
('PowerBank 20K','Electronics',49.00),
('Ergo Chair','Furniture',199.00),
('Standing Desk','Furniture',399.00),
('Office Lamp','Furniture',29.00);

-- Sample orders and items
INSERT INTO orders (order_id, order_date, customer_id, payment_method) VALUES
('ORD000001','2021-05-12','CUST0001','Credit Card'),
('ORD000002','2020-11-03','CUST0002','PayPal');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount, sales, profit) VALUES
('ORD000001', 1, 1, 699.00, 0.05, 664.05, 119.53),
('ORD000002', 2, 2, 49.00, 0.00, 98.00, 17.64);
