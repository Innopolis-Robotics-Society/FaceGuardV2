"""Integration tests for the JSON API endpoints.

Covers:
  GET    /backend/users          — list
  GET    /backend/users/{id}     — fetch one
  PUT    /backend/users/{id}     — update
  DELETE /backend/users/{id}     — delete
  GET    /users/{id}             — HTML detail page
  POST   /users/{id}/update      — HTML form submit
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pytest

from app.database import FaceDatabase


@pytest.fixture
def seeded_client(client) -> object:
    """A TestClient with one permanent user and one temporary user pre-seeded.

    The `client` fixture in conftest.py uses a cached Settings (lru_cache
    on `get_settings`), so all integration tests share the same SQLite
    file. We wipe users + logs before seeding to keep each test
    independent.
    """
    from app.main import app

    db: FaceDatabase = app.state.db

    # Wipe state.
    for u in db.list_users():
        db.delete_user(u.id)
    with db._lock:
        db._conn.execute("DELETE FROM logs")
        db._conn.commit()

    # Seed fresh.
    emb = np.zeros(512, dtype=np.float32)
    emb[0] = 1.0
    db.register_user("Alice Perm", emb, type="permanent")
    expires = datetime.now(UTC) + timedelta(days=5)
    db.register_user("Bob Temp", emb, type="temporary", expires_at=expires)
    return client


def _login(client):
    r = client.post("/login", data={"username": "admin", "password": "testpass"})
    assert r.status_code in (200, 303)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_api_list_users(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users")
    assert r.status_code == 200
    data = r.json()
    names = {u["name"] for u in data["users"]}
    assert "Alice Perm" in names
    assert "Bob Temp" in names


@pytest.mark.integration
def test_api_list_users_filter_by_type(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=temporary")
    assert r.status_code == 200
    data = r.json()
    names = {u["name"] for u in data["users"]}
    assert names == {"Bob Temp"}


@pytest.mark.integration
def test_api_list_users_invalid_type_ignored(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=bogus")
    assert r.status_code == 200
    # Invalid type filter is ignored — returns all users.
    data = r.json()
    assert len(data["users"]) >= 2


@pytest.mark.integration
def test_api_get_user(seeded_client):
    _login(seeded_client)
    # Find Alice's id first.
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.get(f"/backend/users/{alice_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Alice Perm"
    assert data["type"] == "permanent"
    assert data["expires_at"] is None


@pytest.mark.integration
def test_api_get_user_not_found(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users/99999")
    assert r.status_code == 404


@pytest.mark.integration
def test_api_put_update_name(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.put(
        f"/backend/users/{alice_id}",
        json={"name": "Alice Smith"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Alice Smith"
    assert data["type"] == "permanent"


@pytest.mark.integration
def test_api_put_switch_permanent_to_temporary(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    expires = (datetime.now(UTC) + timedelta(days=10)).isoformat()
    r = seeded_client.put(
        f"/backend/users/{alice_id}",
        json={"type": "temporary", "expires_at": expires},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "temporary"
    assert data["expires_at"] is not None


@pytest.mark.integration
def test_api_put_switch_temporary_to_permanent(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=temporary")
    bob_id = r.json()["users"][0]["id"]

    r = seeded_client.put(
        f"/backend/users/{bob_id}",
        json={"type": "permanent"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "permanent"
    assert data["expires_at"] is None


@pytest.mark.integration
def test_api_put_invalid_type(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.put(
        f"/backend/users/{alice_id}",
        json={"type": "bogus"},
    )
    assert r.status_code == 400


@pytest.mark.integration
def test_api_put_temporary_without_expires_and_no_existing(seeded_client):
    """If a permanent user is switched to temporary without expires_at,
    the API must reject it."""
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.put(
        f"/backend/users/{alice_id}",
        json={"type": "temporary"},  # no expires_at, no existing
    )
    assert r.status_code == 400


@pytest.mark.integration
def test_api_put_duplicate_name(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.put(
        f"/backend/users/{alice_id}",
        json={"name": "Bob Temp"},  # already exists
    )
    assert r.status_code == 409


@pytest.mark.integration
def test_api_put_invalid_embedding_size(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.put(
        f"/backend/users/{alice_id}",
        json={"embedding": [0.1, 0.2, 0.3]},  # not 512
    )
    assert r.status_code == 400


@pytest.mark.integration
def test_api_put_not_found(seeded_client):
    _login(seeded_client)
    r = seeded_client.put(
        "/backend/users/99999",
        json={"name": "Nobody"},
    )
    assert r.status_code == 404


@pytest.mark.integration
def test_api_delete_user(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.delete(f"/backend/users/{alice_id}")
    assert r.status_code == 200

    # Verify the user is gone.
    r = seeded_client.get(f"/backend/users/{alice_id}")
    assert r.status_code == 404


@pytest.mark.integration
def test_api_delete_not_found(seeded_client):
    _login(seeded_client)
    r = seeded_client.delete("/backend/users/99999")
    assert r.status_code == 404


@pytest.mark.integration
def test_api_requires_auth(client):
    """All /backend/* endpoints require admin session."""
    r = client.get("/backend/users")
    assert r.status_code in (401, 403)


# ---------------------------------------------------------------------------
# HTML detail page
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_user_detail_page_renders(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.get(f"/users/{alice_id}")
    assert r.status_code == 200
    assert "Alice Perm" in r.text
    assert "permanent" in r.text


@pytest.mark.integration
def test_user_detail_page_not_found(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/users/99999")
    assert r.status_code == 404


@pytest.mark.integration
def test_user_detail_page_shows_expires_for_temporary(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=temporary")
    bob_id = r.json()["users"][0]["id"]

    r = seeded_client.get(f"/users/{bob_id}")
    assert r.status_code == 200
    assert "Bob Temp" in r.text
    assert "temporary" in r.text


@pytest.mark.integration
def test_user_update_form_changes_name(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.post(
        f"/users/{alice_id}/update",
        data={"name": "Alice Renamed", "type": "permanent"},
        follow_redirects=False,
    )
    assert r.status_code == 303  # redirect

    # Verify the change persisted.
    r = seeded_client.get(f"/backend/users/{alice_id}")
    assert r.json()["name"] == "Alice Renamed"


@pytest.mark.integration
def test_user_update_form_switches_to_temporary(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    expires = (datetime.now(UTC) + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M")
    r = seeded_client.post(
        f"/users/{alice_id}/update",
        data={"name": "Alice", "type": "temporary", "expires_at": expires},
        follow_redirects=False,
    )
    assert r.status_code == 303

    r = seeded_client.get(f"/backend/users/{alice_id}")
    data = r.json()
    assert data["type"] == "temporary"
    assert data["expires_at"] is not None


@pytest.mark.integration
def test_user_update_form_temporary_without_expires_400(seeded_client):
    _login(seeded_client)
    r = seeded_client.get("/backend/users?type=permanent")
    alice_id = r.json()["users"][0]["id"]

    r = seeded_client.post(
        f"/users/{alice_id}/update",
        data={"name": "Alice", "type": "temporary"},  # no expires_at
    )
    assert r.status_code == 400


@pytest.mark.integration
def test_users_list_has_links_to_detail(seeded_client):
    """Main user list should link to detail pages."""
    _login(seeded_client)
    r = seeded_client.get("/users")
    assert r.status_code == 200
    # Each user name should be a link to /users/{id}.
    assert 'href="/users/' in r.text
