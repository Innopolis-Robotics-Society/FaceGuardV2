-- FaceGuard SQLite schema.
-- Applied idempotently on backend startup by `app.database.FaceDatabase`.

-- Permanent users (lab workers, employees). Never auto-deleted.
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    UNIQUE NOT NULL,
    embedding   BLOB    NOT NULL,            -- 512-dim float32, normalized
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Temporary guests. Auto-deleted when expires_at < now (during recognize()).
-- Per team decision: NO created_by / created_at columns — only expires_at.
CREATE TABLE IF NOT EXISTS guests (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    embedding   BLOB    NOT NULL,
    expires_at  TIMESTAMP NOT NULL
);

-- Access attempt audit log (US-10).
CREATE TABLE IF NOT EXISTS logs (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    score        REAL,
    access_type  TEXT    CHECK(access_type IN ('user', 'guest', 'unknown')) NOT NULL,
    success      BOOLEAN NOT NULL,
    liveness_passed  BOOLEAN,
    timestamp    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_access_type ON logs(access_type);
CREATE INDEX IF NOT EXISTS idx_logs_liveness ON logs(liveness_passed);

-- Admin accounts for the web UI.
CREATE TABLE IF NOT EXISTS admins (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    username       TEXT    UNIQUE NOT NULL,
    password_hash  TEXT    NOT NULL,         -- bcrypt hash
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
