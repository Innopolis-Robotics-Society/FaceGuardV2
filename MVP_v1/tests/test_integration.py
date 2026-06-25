"""Integration tests for FastAPI routes (TestClient + in-memory DB)."""

from __future__ import annotations

import pytest


@pytest.mark.integration
def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.integration
def test_login_form_renders(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert "login" in resp.text.lower()


@pytest.mark.integration
def test_login_and_logout_flow(client):
    resp = client.post("/login", data={"username": "admin", "password": "testpass"})
    assert resp.status_code in (302, 200)

    if resp.status_code == 302:
        resp = client.get(resp.headers["location"], follow_redirects=True)
    assert resp.status_code == 200

    resp = client.post("/logout")
    assert resp.status_code in (302, 200)

    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (302, 307, 401)
