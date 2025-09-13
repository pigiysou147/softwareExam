-- 示例数据库：含常见含敏感信息的表，便于分级分类

CREATE SCHEMA IF NOT EXISTS public;

-- 用户表（含 PII）
CREATE TABLE IF NOT EXISTS public.users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(32),
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 订单表（含交易信息）
CREATE TABLE IF NOT EXISTS public.orders (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES public.users(id),
  order_number VARCHAR(64) NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  currency VARCHAR(8) DEFAULT 'CNY',
  status VARCHAR(32) DEFAULT 'created',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 支付卡（高敏感）
CREATE TABLE IF NOT EXISTS public.payment_cards (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES public.users(id),
  card_holder_name VARCHAR(128),
  card_number VARCHAR(32),
  expiry_month INT,
  expiry_year INT,
  cvv VARCHAR(8),
  billing_address TEXT
);

-- 产品表（非敏感）
CREATE TABLE IF NOT EXISTS public.products (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  category VARCHAR(64),
  price NUMERIC(10,2) NOT NULL,
  stock INT DEFAULT 0
);

-- 示例数据
INSERT INTO public.users (username, email, phone, password_hash)
VALUES
  ('alice', 'alice@example.com', '13800000001', 'hash1'),
  ('bob', 'bob@example.com', '13800000002', 'hash2')
ON CONFLICT DO NOTHING;

INSERT INTO public.products (name, category, price, stock)
VALUES
  ('Widget A', 'gadget', 99.90, 100),
  ('Widget B', 'gadget', 149.00, 50)
ON CONFLICT DO NOTHING;

INSERT INTO public.orders (user_id, order_number, amount, currency, status)
VALUES
  (1, 'ORD-20250101-0001', 199.80, 'CNY', 'paid');

