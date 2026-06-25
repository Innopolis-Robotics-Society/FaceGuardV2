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
    assert len(s.database_path) > 0


@pytest.mark.qrt
def test_settings_rejects_empty_secret_key():
    with pytest.raises(Exception):
        Settings(SECRET_KEY="")


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("THRESHOLD", "0.65")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    s = Settings()
    assert s.threshold == 0.65
