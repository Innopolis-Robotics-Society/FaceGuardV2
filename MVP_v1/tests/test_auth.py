"""Tests for auth (bcrypt hashing + verification)."""

from __future__ import annotations

import pytest

from app.auth import hash_password, verify_password


@pytest.mark.qrt
def test_hash_and_verify_roundtrip():
    plain = "correct horse battery staple"
    h = hash_password(plain)
    assert h != plain
    assert verify_password(plain, h) is True


@pytest.mark.qrt
def test_verify_rejects_wrong_password():
    h = hash_password("hunter2")
    assert verify_password("wrong", h) is False


def test_hash_is_salt_randomized():
    """Two hashes of the same password differ (bcrypt salt)."""
    a = hash_password("same")
    b = hash_password("same")
    assert a != b
    assert verify_password("same", a) is True
    assert verify_password("same", b) is True


def test_verify_handles_malformed_hash():
    """Should return False, not raise, on a corrupt hash string."""
    assert verify_password("anything", "not-a-hash") is False
    assert verify_password("anything", "") is False
