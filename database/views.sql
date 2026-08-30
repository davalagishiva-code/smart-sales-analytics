USE smart_sales_db;

-- View: monthly sales
CREATE OR REPLACE VIEW view_monthly_sales AS
SELECT DATE_FORMAT(o.order_date, '%Y-%m') AS month, SUM(oi.sales) AS sales, SUM(oi.profit) AS profit
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY month;

-- View: product performance
CREATE OR REPLACE VIEW view_product_performance AS
SELECT p.product_id, p.product_name, p.category, SUM(oi.quantity) AS total_qty, SUM(oi.sales) AS total_sales, SUM(oi.profit) AS total_profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category;
