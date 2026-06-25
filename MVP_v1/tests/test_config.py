"""Unit tests for config (critical module — validation affects all runtime behaviour)."""

from __future__ import annotations

import pytest

from app.config import Settings


def test_settings_default_threshold_in_valid_range():
    s = Settings()
    assert 0.0 < s.threshold <= 1.0


def test_settings_emulated_servo_by_default():
    s = Settings()
    assert s.servo_mode == "emulated"


def test_settings_database_path_is_set():
    s = Settings()
    assert s.database_path is not None
    assert str(s.database_path)


def test_settings_empty_secret_key():
    """pydantic-settings allows empty SecretStr; we document this as bad practice."""
    s = Settings(SECRET_KEY="")
    assert s.secret_key.get_secret_value() == ""


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("THRESHOLD", "0.65")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    s = Settings()
    assert s.threshold == 0.65
