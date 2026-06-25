"""Servo actuator abstraction (US-06, US-07).

Two implementations:
  * `GpioServo` — controls a physical SG90-class servo via `gpiozero`
    on the Raspberry Pi. Used when `SERVO_MODE=gpio`.
  * `EmulatedServo` — logs the open/close transitions and exposes the
    current state for the UI to render. Used when `SERVO_MODE=emulated`
    (i.e. on x86 laptops, or when no servo is connected).

Both share the `Servo` protocol so the recognition loop doesn't care
which one it's talking to.

LED indicators (US from customer feedback: green=granted, red=denied,
yellow=processing) follow the same abstraction. They are toggled by the
recognition loop based on the verdict, not by the servo itself, so they
live in `state.py` and the templates, not here.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Protocol

log = logging.getLogger(__name__)


class Servo(Protocol):
    """Abstract servo interface.

    The recognition loop calls `open()` when access is granted. The
    servo then rotates to the open position, waits for the configured
    duration, and returns to the closed position — that sequence runs
    in a background thread so the recognition loop is never blocked.
    """

    mode: str

    @property
    def is_open(self) -> bool: ...

    def open(self) -> None:
        """Trigger the open → wait → close sequence. Non-blocking."""
        ...

    def close(self) -> None:
        """Force-close immediately (e.g. on shutdown)."""
        ...


class EmulatedServo:
    """Pure-Python servo for x86 development and the laptop emulator.

    Records every state transition so the UI can render the servo
    position alongside the camera stream. No external dependencies.
    """

    mode = "emulated"

    def __init__(self, open_duration_sec: float = 2.0):
        self._open_duration = open_duration_sec
        self._is_open = False
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._last_event: dict[str, str | float] = {
            "action": "closed",
            "at": time.time(),
        }

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def last_event(self) -> dict[str, str | float]:
        return dict(self._last_event)

    def open(self) -> None:
        with self._lock:
            if self._is_open:
                # Already open — restart the timer.
                if self._thread and self._thread.is_alive():
                    return
            self._is_open = True
            self._last_event = {"action": "opened", "at": time.time()}
            log.info("[emulated-servo] OPEN (door unlocked)")
            self._thread = threading.Thread(target=self._auto_close, daemon=True)
            self._thread.start()

    def _auto_close(self) -> None:
        time.sleep(self._open_duration)
        with self._lock:
            self._is_open = False
            self._last_event = {"action": "closed", "at": time.time()}
            log.info("[emulated-servo] CLOSE (door locked again)")

    def close(self) -> None:
        with self._lock:
            self._is_open = False
            self._last_event = {"action": "closed", "at": time.time()}
            log.info("[emulated-servo] forced CLOSE")


class GpioServo:
    """Physical servo on the Raspberry Pi via `gpiozero.AngularServo`.

    Wiring (default BCM 18 / physical pin 12):
        signal  -> Pi GPIO 18 (PWM0)
        VCC     -> 5V (red wire on SG90)
        GND     -> GND

    sg90 safe range: 0° (closed) <-> 90° (open). The servo is held in
    the open position for `open_duration_sec`, then returned to 0°.
    Powering it from the Pi's 5V rail is fine for an SG90 with no load
    (a door lock will draw < 100mA), but if you see brownouts, move
    VCC to an external 5V supply with shared ground.
    """

    mode = "gpio"

    def __init__(
        self,
        pin: int = 18,
        open_duration_sec: float = 2.0,
        open_angle: float = 90.0,
        closed_angle: float = 0.0,
    ):
        # Imported lazily so x86 devs don't need gpiozero installed.
        from gpiozero import AngularServo  # type: ignore[import-not-found]

        self._servo = AngularServo(pin, min_angle=0, max_angle=180)
        self._open_duration = open_duration_sec
        self._open_angle = open_angle
        self._closed_angle = closed_angle
        self._is_open = False
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

        # Start closed.
        self._servo.angle = closed_angle

    @property
    def is_open(self) -> bool:
        return self._is_open

    def open(self) -> None:
        with self._lock:
            if self._is_open and self._thread and self._thread.is_alive():
                return
            self._is_open = True
            self._servo.angle = self._open_angle
            log.info(
                "[gpio-servo] OPEN ( BCM %s -> %s° )",
                self._servo.pin.number if hasattr(self._servo, "pin") else "?",
                self._open_angle,
            )
            self._thread = threading.Thread(target=self._auto_close, daemon=True)
            self._thread.start()

    def _auto_close(self) -> None:
        time.sleep(self._open_duration)
        with self._lock:
            self._servo.angle = self._closed_angle
            self._is_open = False
            log.info("[gpio-servo] CLOSE (return to %s°)", self._closed_angle)

    def close(self) -> None:
        with self._lock:
            self._servo.angle = self._closed_angle
            self._is_open = False


def make_servo(settings) -> Servo:
    """Factory: build the right servo for `settings.servo_mode`."""
    if settings.servo_mode == "gpio":
        try:
            return GpioServo(
                pin=settings.servo_pin,
                open_duration_sec=settings.servo_open_duration_sec,
            )
        except Exception as e:  # pragma: no cover — hardware-dependent
            log.error("Failed to init GpioServo (falling back to emulated): %s", e)
            return EmulatedServo(open_duration_sec=settings.servo_open_duration_sec)
    return EmulatedServo(open_duration_sec=settings.servo_open_duration_sec)
