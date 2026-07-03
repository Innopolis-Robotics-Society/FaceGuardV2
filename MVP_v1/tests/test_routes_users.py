"""Integration tests for user/guest management routes (app/routes/users.py).

Covers: delete user, delete guest, purge expired guests.
Registration is covered separately (requires ML mock with embedding).
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from app.database import FaceDatabase

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _login(client) -> None:
    client.post("/login", data={"username": "admin", "password": "testpass"})


def _rand_emb(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(512).astype(np.float32)
    return v / np.linalg.norm(v)


def _get_db() -> FaceDatabase:
    return FaceDatabase(db_path=os.environ["DATABASE_PATH"])


# ---------------------------------------------------------------------------
# Auth guards
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_delete_user_requires_auth(client):
    resp = client.post("/users/999/delete", follow_redirects=False)
    assert resp.status_code in (302, 307, 401, 403)


@pytest.mark.integration
def test_delete_guest_requires_auth(client):
    resp = client.post("/guests/999/delete", follow_redirects=False)
    assert resp.status_code in (302, 307, 401, 403)


@pytest.mark.integration
def test_purge_guests_requires_auth(client):
    resp = client.post("/guests/purge", follow_redirects=False)
    assert resp.status_code in (302, 307, 401, 403)


# ---------------------------------------------------------------------------
# Delete user
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_delete_existing_user_redirects(client):
    _login(client)
    db = _get_db()
    user = db.register_user("TempUser", _rand_emb(1))
    db.close()

    resp = client.post(f"/users/{user.id}/delete", follow_redirects=False)
    assert resp.status_code in (302, 303)


@pytest.mark.integration
def test_delete_existing_user_removes_from_db(client):
    _login(client)
    db = _get_db()
    user = db.register_user("DeleteMe", _rand_emb(2))
    db.close()

    client.post(f"/users/{user.id}/delete", follow_redirects=True)

    db = _get_db()
    assert db.get_user(user.id) is None
    db.close()


@pytest.mark.integration
def test_delete_nonexistent_user_returns_404(client):
    _login(client)
    resp = client.post("/users/999999/delete", follow_redirects=False)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Delete guest
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_delete_existing_guest_redirects(client):
    _login(client)
    db = _get_db()
    guest = db.register_guest_for_days("TempGuest", _rand_emb(3), days=1)
    db.close()

    resp = client.post(f"/guests/{guest.id}/delete", follow_redirects=False)
    assert resp.status_code in (302, 303)


@pytest.mark.integration
def test_delete_nonexistent_guest_returns_404(client):
    _login(client)
    resp = client.post("/guests/999999/delete", follow_redirects=False)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Purge expired guests
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_purge_returns_count(client):
    _login(client)
    db = _get_db()
    past = datetime.now(UTC) - timedelta(hours=2)
    db.register_guest("Expired1", _rand_emb(10), past)
    db.register_guest("Expired2", _rand_emb(11), past)
    db.register_guest_for_days("Active", _rand_emb(12), days=1)
    db.close()

    resp = client.post("/guests/purge")
    assert resp.status_code == 200
    assert resp.json()["purged"] == 2


@pytest.mark.integration
def test_purge_zero_when_no_expired(client):
    _login(client)
    resp = client.post("/guests/purge")
    assert resp.status_code == 200
    assert resp.json()["purged"] == 0
