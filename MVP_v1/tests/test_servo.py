"""Tests for the emulated servo."""

from __future__ import annotations

import time

import pytest

from app.servo import EmulatedServo, make_servo


def test_emulated_servo_starts_closed():
    s = EmulatedServo(open_duration_sec=0.05)
    assert s.is_open is False
    assert s.mode == "emulated"


@pytest.mark.qrt
def test_emulated_servo_opens_then_closes():
    s = EmulatedServo(open_duration_sec=0.05)
    s.open()
    assert s.is_open is True
    time.sleep(0.1)
    assert s.is_open is False
    assert s.last_event["action"] == "closed"


def test_emulated_servo_force_close():
    s = EmulatedServo(open_duration_sec=1.0)
    s.open()
    assert s.is_open is True
    s.close()
    assert s.is_open is False


def test_make_servo_returns_emulated_by_default():
    class FakeSettings:
        servo_mode = "emulated"
        servo_pin = 18
        servo_open_duration_sec = 0.5

    s = make_servo(FakeSettings())
    assert s.mode == "emulated"


@pytest.mark.qrt
def test_make_servo_falls_back_when_gpio_unavailable(monkeypatch):
    """On x86, gpiozero isn't installed - make_servo must fall back gracefully"""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "gpiozero":
            raise ImportError("no gpiozero on x86")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    class FakeSettings:
        servo_mode = "gpio"
        servo_pin = 18
        servo_open_duration_sec = 0.5

    s = make_servo(FakeSettings())
    assert s.mode == "emulated"
