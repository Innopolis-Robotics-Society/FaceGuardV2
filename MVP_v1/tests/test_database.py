"""Tests for FaceDatabase (issue #29 — data access layer).

Covers:
- Schema bootstrap on a fresh DB.
- User CRUD.
- Guest CRUD + lazy expiry purge.
- recognize() returns correct verdict for users, guests, expired guests,
  and unknown probes.
- Audit log is written on every recognize() call.
- Admin bootstrap is idempotent.

Embeddings here are synthetic — we only test data-layer behaviour, not
ML model quality.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from app.database import FaceDatabase


@pytest.fixture
def db(tmp_path) -> FaceDatabase:
    """Fresh in-memory-ish SQLite file per test (in a tmp dir)."""
    db_path = tmp_path / "test.db"
    instance = FaceDatabase(db_path=db_path)
    yield instance
    instance.close()


def _rand_embedding(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(512).astype(np.float32)
    return v / np.linalg.norm(v)


# ---------------------------------------------------------------------------
# Schema + bootstrap
# ---------------------------------------------------------------------------


def test_schema_applied_on_init(db: FaceDatabase):
    counts = db.counts()
    assert counts == {"users": 0, "active_guests": 0, "logs": 0}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


def test_register_user_returns_user_with_id_and_embedding(db: FaceDatabase):
    emb = _rand_embedding(1)
    user = db.register_user("Alice", emb)
    assert user.id is not None
    assert user.name == "Alice"
    assert user.embedding.shape == (512,)
    np.testing.assert_allclose(user.embedding, emb, rtol=1e-6)
    assert user.created_at.tzinfo is not None  # aware


def test_register_user_duplicate_name_raises(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1))
    with pytest.raises(Exception):  # sqlite3.IntegrityError
        db.register_user("Alice", _rand_embedding(2))


def test_list_users_ordered_by_name(db: FaceDatabase):
    db.register_user("Zara", _rand_embedding(1))
    db.register_user("Alice", _rand_embedding(2))
    db.register_user("Bob", _rand_embedding(3))
    names = [u.name for u in db.list_users()]
    assert names == ["Alice", "Bob", "Zara"]


def test_delete_user(db: FaceDatabase):
    user = db.register_user("Alice", _rand_embedding(1))
    assert db.delete_user(user.id) is True
    assert db.get_user(user.id) is None
    assert db.delete_user(user.id) is False  # already gone


# ---------------------------------------------------------------------------
# Guests
# ---------------------------------------------------------------------------


def test_register_guest_for_days_sets_correct_expiry(db: FaceDatabase):
    before = datetime.now(UTC)
    guest = db.register_guest_for_days("Courier", _rand_embedding(1), days=7)
    after = datetime.now(UTC)

    # Expiry should be ~7 days from now.
    assert before + timedelta(days=7) <= guest.expires_at <= after + timedelta(days=7)


def test_list_guests_excludes_expired_by_default(db: FaceDatabase):
    # Active guest (expires in 1 day).
    db.register_guest_for_days("Active", _rand_embedding(1), days=1)
    # Expired guest (expires in the past).
    past = datetime.now(UTC) - timedelta(hours=1)
    db.register_guest("Expired", _rand_embedding(2), past)

    visible = db.list_guests()
    assert [g.name for g in visible] == ["Active"]

    all_guests = db.list_guests(include_expired=True)
    assert {g.name for g in all_guests} == {"Active", "Expired"}


def test_purge_expired_guests_returns_count(db: FaceDatabase):
    past = datetime.now(UTC) - timedelta(hours=1)
    db.register_guest("A", _rand_embedding(1), past)
    db.register_guest("B", _rand_embedding(2), past)
    db.register_guest_for_days("C", _rand_embedding(3), days=1)

    n = db.purge_expired_guests()
    assert n == 2
    assert [g.name for g in db.list_guests(include_expired=True)] == ["C"]


# ---------------------------------------------------------------------------
# recognize()
# ---------------------------------------------------------------------------


@pytest.mark.qrt
def test_recognize_matches_registered_user_above_threshold(db: FaceDatabase):
    emb = _rand_embedding(42)
    db.register_user("Alice", emb)

    # Probe = same embedding (cosine sim should be 1.0).
    result = db.recognize(emb, threshold=0.5)
    assert result.name == "Alice"
    assert result.access_type == "user"
    assert result.score >= 0.99
    assert result.matched_user_id is not None


@pytest.mark.qrt
def test_recognize_returns_unknown_below_threshold(db: FaceDatabase):
    db.register_user("Alice", _rand_embedding(1))
    probe = _rand_embedding(999)  # very different
    result = db.recognize(probe, threshold=0.9)
    assert result.name == "Unknown"
    assert result.access_type == "unknown"
    assert result.matched_user_id is None


@pytest.mark.qrt
def test_recognize_picks_best_match_when_multiple_users(db: FaceDatabase):
    alice_emb = _rand_embedding(1)
    bob_emb = _rand_embedding(2)
    db.register_user("Alice", alice_emb)
    db.register_user("Bob", bob_emb)

    # Probe = Bob's embedding.
    result = db.recognize(bob_emb, threshold=0.5)
    assert result.name == "Bob"
    assert result.access_type == "user"


@pytest.mark.qrt
def test_recognize_ignores_expired_guests(db: FaceDatabase):
    """An expired guest must NOT match — and must be purged during the call."""
    past = datetime.now(UTC) - timedelta(hours=1)
    expired_emb = _rand_embedding(5)
    db.register_guest("OldVisitor", expired_emb, past)

    # Probe = expired guest's exact embedding. Should NOT match.
    result = db.recognize(expired_emb, threshold=0.3)
    assert result.name == "Unknown"
    assert result.access_type == "unknown"


@pytest.mark.qrt
def test_recognize_matches_active_guest(db: FaceDatabase):
    guest_emb = _rand_embedding(7)
    db.register_guest_for_days("Visitor", guest_emb, days=1)

    result = db.recognize(guest_emb, threshold=0.5)
    assert result.name == "Visitor"
    assert result.access_type == "guest"


@pytest.mark.qrt
def test_recognize_writes_audit_log(db: FaceDatabase):
    emb = _rand_embedding(1)
    db.register_user("Alice", emb)

    # Granted attempt.
    db.recognize(emb, threshold=0.5)
    # Denied attempt.
    db.recognize(_rand_embedding(999), threshold=0.99)

    logs = db.list_logs(limit=10)
    assert len(logs) == 2

    # Most recent first.
    denied = logs[0]
    assert denied.success is False
    assert denied.access_type == "unknown"

    granted = logs[1]
    assert granted.success is True
    assert granted.access_type == "user"
    assert granted.name == "Alice"


def test_recognize_normalizes_probe_vector(db: FaceDatabase):
    """Even if the probe is not normalized, recognize() must compare correctly."""
    emb = _rand_embedding(3)
    db.register_user("Alice", emb)

    # Scale up by 10x — cosine sim should still be 1.0.
    probe = emb * 10.0
    result = db.recognize(probe, threshold=0.5)
    assert result.name == "Alice"
    assert result.score >= 0.99


# ---------------------------------------------------------------------------
# Admins
# ---------------------------------------------------------------------------


def test_bootstrap_admin_is_idempotent(db: FaceDatabase):
    a1 = db.bootstrap_admin("admin", "hash-1")
    a2 = db.bootstrap_admin("admin", "hash-2")  # different hash, same username
    assert a1.id == a2.id
    # The original hash is preserved — second call is a no-op.
    assert a2.password_hash == "hash-1"


def test_get_admin_by_username(db: FaceDatabase):
    db.add_admin("alice", "secret-hash")
    found = db.get_admin_by_username("alice")
    assert found is not None
    assert found.password_hash == "secret-hash"

    assert db.get_admin_by_username("nobody") is None


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------


def test_list_logs_filters_by_name(db: FaceDatabase):
    db.add_log("Alice", 0.9, "user", True)
    db.add_log("Bob", 0.3, "unknown", False)
    db.add_log("Alice", 0.85, "user", True)

    only_alice = db.list_logs(user_filter="Alice")
    assert len(only_alice) == 2
    assert all(e.name == "Alice" for e in only_alice)


def test_list_logs_today_filter_isolates_old_entries(db: FaceDatabase, tmp_path):
    """We insert an old entry directly via SQL to test DATE() filtering."""
    import sqlite3

    conn = sqlite3.connect(str(tmp_path / "test.db"))
    # Don't re-create the schema — the FaceDatabase already did.
    conn.close()

    db.add_log("Alice", 0.9, "user", True)

    # Insert a row with a 5-day-old timestamp directly.
    with db._lock:
        db._conn.execute(
            "INSERT INTO logs (name, score, access_type, success, timestamp) "
            "VALUES (?, ?, ?, ?, ?)",
            ("Bob", 0.3, "unknown", False, "2020-01-01 12:00:00"),
        )
        db._conn.commit()

    today = db.list_logs(today_only=True)
    assert len(today) == 1
    assert today[0].name == "Alice"

    all_logs = db.list_logs(today_only=False)
    assert len(all_logs) == 2
