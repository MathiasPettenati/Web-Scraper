CREATE TABLE IF NOT EXISTS dealers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    currency TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    reliability_score NUMERIC(3, 2) DEFAULT 0.90,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    color TEXT,
    condition TEXT,
    store TEXT NOT NULL,
    country TEXT NOT NULL,
    currency TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    original_price NUMERIC(10, 2),
    discount_percent INTEGER,
    sizes TEXT[],
    shipping_cost NUMERIC(10, 2),
    shipping_time TEXT,
    rating NUMERIC(3, 2),
    popularity INTEGER,
    in_stock BOOLEAN DEFAULT TRUE,
    verified BOOLEAN DEFAULT TRUE,
    availability TEXT,
    source_url TEXT,
    last_verified DATE,
    image_url TEXT,
    description TEXT,
    tags TEXT[],
    location_hint TEXT,
    deal_score NUMERIC(6, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    product_id TEXT REFERENCES products(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    threshold_percent INTEGER NOT NULL,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
