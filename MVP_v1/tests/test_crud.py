"""Tests for issue #76 — unified user table, CRUD, type switching."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from app.database import FaceDatabase


@pytest.fixture
def db(tmp_path) -> FaceDatabase:
    db_path = tmp_path / "test.db"
    instance = FaceDatabase(db_path=db_path)
    yield instance
    instance.close()


def _rand_embedding(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(512).astype(np.float32)
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------------------
# Unified schema
# ---------------------------------------------------------------------------


def test_schema_has_unified_users_table(db: FaceDatabase):
    """Issue #76 — single users table with type column, no separate guests table."""
    with db._lock:
        tables = {
            row["name"]
            for row in db._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert "users" in tables
    assert "guests" not in tables, "legacy guests table should not exist"

    with db._lock:
        cols = {
            row["name"]
            for row in db._conn.execute("PRAGMA table_info(users)").fetchall()
        }
    assert "type" in cols
    assert "expires_at" in cols


def test_legacy_two_tables_are_migrated(tmp_path):
    """Pre-#76 databases with separate users + guests tables are migrated
    automatically on startup."""
    db_path = tmp_path / "legacy.db"
    # Build the legacy schema by hand.
    conn = sqlite3.connect(str(db_path))
    conn.executescript(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            embedding BLOB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            embedding BLOB NOT NULL,
            expires_at TIMESTAMP NOT NULL
        );
        INSERT INTO users (name, embedding) VALUES ('Alice', X'01020304');
        INSERT INTO guests (name, embedding, expires_at)
            VALUES ('Bob', X'05060708', '2099-01-01 00:00:00');
        """
    )
    conn.commit()
    conn.close()

    # Now open with FaceDatabase — should migrate.
    db = FaceDatabase(db_path=db_path)
    users = db.list_users()
    names = {u.name for u in users}
    assert names == {"Alice", "Bob"}

    alice = db.get_user_by_name("Alice")
    assert alice.type == "permanent"
    assert alice.expires_at is None

    bob = db.get_user_by_name("Bob")
    assert bob.type == "temporary"
    assert bob.expires_at is not None

    # Legacy guests table must be gone.
    with db._lock:
        tables = {
            row["name"]
            for row in db._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    assert "guests" not in tables
    db.close()


# ---------------------------------------------------------------------------
# CRUD — Create / Read / Update / Delete
# ---------------------------------------------------------------------------


def test_register_permanent_user(db: FaceDatabase):
    u = db.register_user("Alice", _rand_embedding(1), type="permanent")
    assert u.id is not None
    assert u.name == "Alice"
    assert u.type == "permanent"
    assert u.expires_at is None


def test_register_temporary_user(db: FaceDatabase):
    expires = datetime.now(UTC) + timedelta(days=7)
    u = db.register_user(
        "Bob", _rand_embedding(2), type="temporary", expires_at=expires
    )
    assert u.type == "temporary"
    assert u.expires_at is not None
    assert abs((u.expires_at - expires).total_seconds()) < 5


def test_register_temporary_without_expires_raises(db: FaceDatabase):
    with pytest.raises(ValueError, match="temporary users require expires_at"):
        db.register_user("Bob", _rand_embedding(2), type="temporary")


def test_register_invalid_type_raises(db: FaceDatabase):
    with pytest.raises(ValueError, match="invalid user type"):
        db.register_user("X", _rand_embedding(2), type="bogus")  # type: ignore[arg-type]


def test_register_duplicate_name_raises(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1))
    with pytest.raises(sqlite3.IntegrityError):
        db.register_user("Alice", _rand_embedding(2))


def test_get_user_returns_none_for_missing(db: FaceDatabase):
    assert db.get_user(99999) is None


def test_get_user_by_name(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1))
    u = db.get_user_by_name("Alice")
    assert u is not None
    assert u.name == "Alice"


def test_list_users_all(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1), type="permanent")
    db.register_user(
        "Bob", _rand_embedding(2), type="temporary",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    users = db.list_users()
    assert {u.name for u in users} == {"Alice", "Bob"}


def test_list_users_filter_by_type(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1), type="permanent")
    db.register_user(
        "Bob", _rand_embedding(2), type="temporary",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )
    permanent = db.list_users(type_filter="permanent")
    assert {u.name for u in permanent} == {"Alice"}
    temporary = db.list_users(type_filter="temporary")
    assert {u.name for u in temporary} == {"Bob"}


def test_list_users_excludes_expired_temporary(db: FaceDatabase):
    db.register_user("Active", _rand_embedding(1), type="permanent")
    db.register_user(
        "Expired", _rand_embedding(2), type="temporary",
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )
    visible = db.list_users(include_expired=False)
    assert {u.name for u in visible} == {"Active"}


def test_delete_user(db: FaceDatabase):
    u = db.register_user("Alice", _rand_embedding(1))
    assert db.delete_user(u.id) is True
    assert db.get_user(u.id) is None
    assert db.delete_user(u.id) is False


# ---------------------------------------------------------------------------
# Type switching — issue #76 core requirement
# ---------------------------------------------------------------------------


def test_switch_permanent_to_temporary(db: FaceDatabase):
    u = db.register_user("Alice", _rand_embedding(1), type="permanent")
    expires = datetime.now(UTC) + timedelta(days=3)
    updated = db.update_user(u.id, type="temporary", expires_at=expires)
    assert updated is not None
    assert updated.type == "temporary"
    assert updated.expires_at is not None


def test_switch_temporary_to_permanent_clears_expires(db: FaceDatabase):
    expires = datetime.now(UTC) + timedelta(days=3)
    u = db.register_user(
        "Bob", _rand_embedding(1), type="temporary", expires_at=expires
    )
    updated = db.update_user(u.id, type="permanent")
    assert updated is not None
    assert updated.type == "permanent"
    assert updated.expires_at is None


def test_update_name(db: FaceDatabase):
    u = db.register_user("Alice", _rand_embedding(1))
    updated = db.update_user(u.id, name="Alice Smith")
    assert updated is not None
    assert updated.name == "Alice Smith"


def test_update_name_to_existing_raises(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1))
    bob = db.register_user("Bob", _rand_embedding(2))
    with pytest.raises(sqlite3.IntegrityError):
        db.update_user(bob.id, name="Alice")


def test_update_embedding(db: FaceDatabase):
    u = db.register_user("Alice", _rand_embedding(1))
    new_emb = _rand_embedding(99)
    updated = db.update_user(u.id, embedding=new_emb)
    assert updated is not None
    np.testing.assert_allclose(updated.embedding, new_emb, rtol=1e-6)


def test_update_nonexistent_returns_none(db: FaceDatabase):
    assert db.update_user(99999, name="Nobody") is None


def test_update_invalid_type_raises(db: FaceDatabase):
    u = db.register_user("Alice", _rand_embedding(1))
    with pytest.raises(ValueError, match="invalid user type"):
        db.update_user(u.id, type="bogus")  # type: ignore[arg-type]


def test_update_temporary_without_expires_keeps_existing(db: FaceDatabase):
    """If user is already temporary, update without expires_at should
    preserve the existing expires_at."""
    expires = datetime.now(UTC) + timedelta(days=3)
    u = db.register_user(
        "Bob", _rand_embedding(1), type="temporary", expires_at=expires
    )
    # Change only name — expires_at should be preserved.
    updated = db.update_user(u.id, name="Bob Smith")
    assert updated is not None
    assert updated.name == "Bob Smith"
    assert updated.type == "temporary"
    assert updated.expires_at is not None


# ---------------------------------------------------------------------------
# Backward compatibility — legacy guest API still works
# ---------------------------------------------------------------------------


def test_register_guest_for_days_backward_compat(db: FaceDatabase):
    g = db.register_guest_for_days("Courier", _rand_embedding(1), days=7)
    assert g.type == "temporary"
    assert g.expires_at is not None


def test_list_guests_backward_compat(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1), type="permanent")
    db.register_guest_for_days("Bob", _rand_embedding(2), days=1)
    guests = db.list_guests()
    assert {g.name for g in guests} == {"Bob"}


def test_purge_expired_purges_only_temporary(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1), type="permanent")
    db.register_user(
        "Bob", _rand_embedding(2), type="temporary",
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )
    n = db.purge_expired()
    assert n == 1
    users = db.list_users()
    assert {u.name for u in users} == {"Alice"}


# ---------------------------------------------------------------------------
# Issue #79 — log rotation
# ---------------------------------------------------------------------------


def test_purge_old_logs_deletes_old_entries(db: FaceDatabase):
    db.add_log("Alice", 0.9, "user", True)
    # Insert a row with an old timestamp directly.
    with db._lock:
        db._conn.execute(
            "INSERT INTO logs (name, score, access_type, success, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Bob", 0.3, "unknown", False, "2020-01-01 12:00:00"),
        )
        db._conn.commit()

    n = db.purge_old_logs(days=30)
    assert n == 1
    logs = db.list_logs(limit=10)
    assert len(logs) == 1
    assert logs[0].name == "Alice"


def test_purge_old_logs_default_30_days(db: FaceDatabase):
    # 10-day-old entry should NOT be purged with default 30-day retention.
    with db._lock:
        db._conn.execute(
            "INSERT INTO logs (name, score, access_type, success, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Bob", 0.3, "unknown", False,
             (datetime.now(UTC) - timedelta(days=10)).strftime("%Y-%m-%d %H:%M:%S")),
        )
        db._conn.commit()
    n = db.purge_old_logs()
    assert n == 0


# ---------------------------------------------------------------------------
# Issue #79 — recognize() logs transitions only
# ---------------------------------------------------------------------------


def test_recognize_logs_only_transitions(db: FaceDatabase):
    emb = _rand_embedding(1)
    db.register_user("Alice", emb)

    # First call — state transition (no prior state) → logs.
    db.recognize(emb, threshold=0.5)
    # Second call — same state → no log.
    db.recognize(emb, threshold=0.5)
    # Third call — same state → no log.
    db.recognize(emb, threshold=0.5)

    # Now switch to a denied probe — different state → logs.
    db.recognize(_rand_embedding(999), threshold=0.99)
    # Same denied state — no log.
    db.recognize(_rand_embedding(998), threshold=0.99)

    logs = db.list_logs(limit=20)
    # Expected: 2 log entries (1 granted + 1 denied transition).
    assert len(logs) == 2
    assert logs[0].access_type == "unknown"  # most recent
    assert logs[1].access_type == "user"


def test_recognize_force_log_every_call(db: FaceDatabase):
    """log_transitions_only=False preserves the old every-call behaviour."""
    emb = _rand_embedding(1)
    db.register_user("Alice", emb)
    db.reset_recognize_state()

    db.recognize(emb, threshold=0.5, log_transitions_only=False)
    db.recognize(emb, threshold=0.5, log_transitions_only=False)
    db.recognize(emb, threshold=0.5, log_transitions_only=False)

    logs = db.list_logs(limit=20)
    assert len(logs) == 3


def test_recognize_works_with_unified_table(db: FaceDatabase):
    """End-to-end: register permanent + temporary, recognize each."""
    perm_emb = _rand_embedding(1)
    temp_emb = _rand_embedding(2)
    db.register_user("Alice", perm_emb, type="permanent")
    db.register_user(
        "Bob", temp_emb, type="temporary",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )

    # Recognize Alice.
    db.reset_recognize_state()
    r1 = db.recognize(perm_emb, threshold=0.5)
    assert r1.name == "Alice"
    assert r1.access_type == "user"

    # Recognize Bob.
    db.reset_recognize_state()
    r2 = db.recognize(temp_emb, threshold=0.5)
    assert r2.name == "Bob"
    assert r2.access_type == "guest"


def test_recognize_ignores_expired_temporary(db: FaceDatabase):
    """Expired temporary users are purged and not matched."""
    expired_emb = _rand_embedding(5)
    db.register_user(
        "OldVisitor", expired_emb, type="temporary",
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )

    db.reset_recognize_state()
    r = db.recognize(expired_emb, threshold=0.3)
    assert r.name == "Unknown"
    assert r.access_type == "unknown"
