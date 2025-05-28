-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- Diary entries
CREATE TABLE IF NOT EXISTS diary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    entry_type TEXT NOT NULL,
    content TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Add privacy column to diary entries (run only if needed)
-- NOTE: Only run this once. You can comment it out after it's added.
ALTER TABLE diary_entries ADD COLUMN is_private INTEGER DEFAULT 0;

-- Balaa history
CREATE TABLE IF NOT EXISTS balaa_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    fare REAL,
    group_size INTEGER,
    amounts TEXT,
    expected REAL,
    received REAL,
    change REAL,
    time TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
