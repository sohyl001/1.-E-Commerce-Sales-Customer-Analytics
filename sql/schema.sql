-- ====================================================================
-- E-Commerce Sales & Customer Analytics Database Schema (SQLite / ANSI SQL)
-- ====================================================================

-- Safely drop child tables before parent tables to respect foreign keys
PRAGMA foreign_keys = OFF;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS categories;
PRAGMA foreign_keys = ON;

-- 1. Dim Categories (Parent Table)
CREATE TABLE categories (
    category_id VARCHAR(20) PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    description TEXT
);

-- 2. Dim Products (References Categories)
CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category_id VARCHAR(20) NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    target_margin_pct DECIMAL(5, 2) NOT NULL,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 3. Dim Customers (Parent Table)
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL DEFAULT 'United States',
    signup_date DATE NOT NULL,
    acquisition_channel VARCHAR(50) NOT NULL,  -- Organic, Paid Search, Social Media, Referral, Email
    customer_tier VARCHAR(20) DEFAULT 'Standard' -- Standard, Silver, Gold, Platinum
);

-- 4. Fact Orders (References Customers)
CREATE TABLE orders (
    order_id VARCHAR(30) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    order_date TIMESTAMP NOT NULL,
    order_status VARCHAR(20) NOT NULL,       -- Completed, Shipped, Cancelled, Returned
    payment_method VARCHAR(30) NOT NULL,     -- Credit Card, PayPal, Apple Pay, BNPL
    sales_channel VARCHAR(30) NOT NULL,      -- Web, Mobile App, Affiliate
    shipping_cost DECIMAL(10, 2) DEFAULT 0.00,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 5. Fact Order Items (References Orders and Products)
CREATE TABLE order_items (
    order_item_id VARCHAR(40) PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    discount_applied DECIMAL(10, 2) DEFAULT 0.00,
    total_item_price DECIMAL(10, 2) NOT NULL, -- (quantity * unit_price) - discount_applied
    gross_profit DECIMAL(10, 2) NOT NULL,     -- total_item_price - (quantity * unit_cost)
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Indexes for high query performance
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(order_status);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);
