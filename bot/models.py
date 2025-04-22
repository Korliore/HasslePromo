CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    username TEXT,
    balance INTEGER DEFAULT 0,
    registered_at TIMESTAMP DEFAULT NOW(),
    ref_code TEXT,
    has_sent_screenshot BOOLEAN DEFAULT FALSE,
    quest_lvl INTEGER DEFAULT 1,
    payout_details TEXT  -- 🆕 информация о выплатах, может быть JSON, IBAN, карта — что угодно
);
"""

CREATE_SCREENSHOTS_TABLE = """
CREATE TABLE IF NOT EXISTS screenshots (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id),
    file_id TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""
