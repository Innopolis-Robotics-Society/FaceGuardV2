"""Unit tests for config (critical module — validation affects all runtime behaviour)."""

from __future__ import annotations

from app.config import Settings


def test_settings_default_threshold_in_valid_range():
    s = Settings(SERVO_OPEN_DURATION_SEC=0.5)
    assert 0.0 < s.threshold <= 1.0


def test_settings_emulated_servo_by_default():
    s = Settings(SERVO_OPEN_DURATION_SEC=0.5)
    assert s.servo_mode == "emulated"


def test_settings_database_path_is_set():
    s = Settings(SERVO_OPEN_DURATION_SEC=0.5)
    assert s.database_path is not None
    assert str(s.database_path) != ""


def test_settings_loads_from_env(monkeypatch):
    monkeypatch.setenv("THRESHOLD", "0.65")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    s = Settings(SERVO_OPEN_DURATION_SEC=0.5)
    assert s.threshold == 0.65
