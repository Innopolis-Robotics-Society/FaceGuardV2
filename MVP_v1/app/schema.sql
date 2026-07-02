-- FaceGuard SQLite schema.
-- Applied idempotently on backend startup by `app.database.FaceDatabase`.
--
-- Issue #76: users and guests are unified into a single `users` table
-- with a `type` column ('permanent' | 'temporary') and a nullable
-- `expires_at` column (only set when type = 'temporary').
-- Migration from the legacy two-table layout is handled in
-- `FaceDatabase._apply_schema()`.

CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    UNIQUE NOT NULL,
    embedding   BLOB    NOT NULL,            -- 512-dim float32, L2-normalized
    type        TEXT    NOT NULL DEFAULT 'permanent'
                        CHECK(type IN ('permanent', 'temporary')),
    expires_at  TIMESTAMP,                   -- NULL for permanent; set for temporary
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast filtering by type and for expiry-based purges.
CREATE INDEX IF NOT EXISTS idx_users_type       ON users(type);
CREATE INDEX IF NOT EXISTS idx_users_expires_at ON users(expires_at);

-- Access attempt audit log (US-10).
CREATE TABLE IF NOT EXISTS logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    score        REAL,
    access_type  TEXT    CHECK(access_type IN ('user', 'guest', 'unknown')) NOT NULL,
    success      BOOLEAN NOT NULL,
    timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp   ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_access_type ON logs(access_type);

-- Admin accounts for the web UI.
CREATE TABLE IF NOT EXISTS admins (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT    UNIQUE NOT NULL,
    password_hash  TEXT    NOT NULL,         -- bcrypt hash
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
