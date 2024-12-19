-- Users table to store user information
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT,
    role TEXT CHECK (role IN ('Admin', 'Staff', 'Student')),
    contact_info TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- Categories table for asset categorization
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    parent_category_id INTEGER,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- Locations table to store building and room information
CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    building TEXT NOT NULL,
    room_number TEXT NOT NULL,
    UNIQUE(building, room_number)
);

-- Assets table to store all asset information
CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    brand TEXT,
    model_number TEXT,
    serial_number TEXT UNIQUE,
    purchase_date TEXT,
    purchase_price REAL,
    condition TEXT CHECK (condition IN ('New', 'Good', 'Fair', 'Poor')),
    location_id INTEGER,
    assigned_to INTEGER,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);

-- Asset transactions table for check-ins and check-outs
CREATE TABLE IF NOT EXISTS asset_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    transaction_type TEXT CHECK (transaction_type IN ('check_out', 'check_in')),
    checkout_date TEXT,
    expected_return_date TEXT,
    actual_return_date TEXT,
    condition_on_return TEXT CHECK (condition_on_return IN ('New', 'Good', 'Fair', 'Poor')),
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Settings table for system configuration
CREATE TABLE IF NOT EXISTS settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_name TEXT NOT NULL UNIQUE,
    setting_value TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes for improved query performance
CREATE INDEX IF NOT EXISTS idx_assets_category ON assets(category_id);
CREATE INDEX IF NOT EXISTS idx_assets_location ON assets(location_id);
CREATE INDEX IF NOT EXISTS idx_assets_assigned_to ON assets(assigned_to);
CREATE INDEX IF NOT EXISTS idx_transactions_asset ON asset_transactions(asset_id);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON asset_transactions(user_id);

-- Insert default categories
INSERT OR IGNORE INTO categories (name) VALUES 
    ('Computer'),
    ('Peripheral'),
    ('Software'),
    ('Furniture');

-- Insert default user roles into settings
INSERT OR IGNORE INTO settings (setting_name, setting_value) VALUES 
    ('allowed_roles', 'Admin,Staff,Student'),
    ('low_stock_threshold', '5'),
    ('default_loan_period_days', '14');

-- Trigger to update the updated_at timestamp for assets
CREATE TRIGGER IF NOT EXISTS update_asset_timestamp 
    AFTER UPDATE ON assets
BEGIN
    UPDATE assets SET updated_at = datetime('now') WHERE asset_id = NEW.asset_id;
END;

-- Trigger to update the updated_at timestamp for settings
CREATE TRIGGER IF NOT EXISTS update_setting_timestamp 
    AFTER UPDATE ON settings
BEGIN
    UPDATE settings SET updated_at = datetime('now') WHERE setting_id = NEW.setting_id;
END;
