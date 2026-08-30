USE smart_sales_db;

-- Total sales
SELECT SUM(sales) AS total_sales FROM order_items;

-- Total profit
SELECT SUM(profit) AS total_profit FROM order_items;

-- Total orders
SELECT COUNT(*) AS total_orders FROM orders;

-- Average order value (AOV)
SELECT (SUM(oi.sales) / COUNT(DISTINCT o.order_id)) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id;

-- Best-selling products by quantity
SELECT p.product_name, SUM(oi.quantity) AS total_qty
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_qty DESC
LIMIT 10;

-- Most profitable products
SELECT p.product_name, SUM(oi.profit) AS total_profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_name
ORDER BY total_profit DESC
LIMIT 10;

-- Sales by region
SELECT r.name AS region, SUM(oi.sales) AS sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN customers c ON o.customer_id = c.customer_id
JOIN regions r ON c.region_id = r.region_id
GROUP BY r.name;

-- Monthly sales (year-month)
SELECT DATE_FORMAT(o.order_date, '%Y-%m') AS month, SUM(oi.sales) AS sales
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;

-- Category performance
SELECT p.category, SUM(oi.sales) AS sales, SUM(oi.profit) AS profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY sales DESC;

-- Customer purchase behavior (top customers)
SELECT c.customer_id, c.customer_name, COUNT(DISTINCT o.order_id) AS orders_count, SUM(oi.sales) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC
LIMIT 20;
