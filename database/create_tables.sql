-- Table schemas will be added here in Step 4.
-- Example table: customers, products, orders, order_items, regions, payments
-- Create regions table
CREATE TABLE IF NOT EXISTS regions (
	region_id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Create customers table
CREATE TABLE IF NOT EXISTS customers (
	customer_id VARCHAR(20) PRIMARY KEY,
	customer_name VARCHAR(100) NOT NULL,
	region_id INT,
	FOREIGN KEY (region_id) REFERENCES regions(region_id)
) ENGINE=InnoDB;

-- Create products table
CREATE TABLE IF NOT EXISTS products (
	product_id INT AUTO_INCREMENT PRIMARY KEY,
	product_name VARCHAR(150) NOT NULL,
	category VARCHAR(100),
	unit_price DECIMAL(10,2)
) ENGINE=InnoDB;

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
	order_id VARCHAR(20) PRIMARY KEY,
	order_date DATE NOT NULL,
	customer_id VARCHAR(20),
	payment_method VARCHAR(50),
	FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
) ENGINE=InnoDB;

-- Create order_items table
CREATE TABLE IF NOT EXISTS order_items (
	id INT AUTO_INCREMENT PRIMARY KEY,
	order_id VARCHAR(20),
	product_id INT,
	quantity INT DEFAULT 1,
	unit_price DECIMAL(10,2),
	discount DECIMAL(5,2) DEFAULT 0.0,
	sales DECIMAL(12,2),
	profit DECIMAL(12,2),
	FOREIGN KEY (order_id) REFERENCES orders(order_id),
	FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;

-- Indexes for faster aggregation queries
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_customers_region ON customers(region_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

