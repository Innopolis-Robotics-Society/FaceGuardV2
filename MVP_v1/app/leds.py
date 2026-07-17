"""LED indicator control for Raspberry Pi GPIO."""
import logging
import threading
from typing import Protocol

log = logging.getLogger(__name__)


class LEDController(Protocol):
    mode: str

    def green_on(self) -> None: ...
    def green_off(self) -> None: ...
    def red_on(self) -> None: ...
    def red_off(self) -> None: ...
    def yellow_on(self) -> None: ...
    def yellow_off(self) -> None: ...
    def all_off(self) -> None: ...


class EmulatedLEDs:
    mode = "emulated"

    def green_on(self):
        log.info("[leds] GREEN ON (access granted)")

    def green_off(self):
        log.info("[leds] GREEN OFF")

    def red_on(self):
        log.info("[leds] RED ON (access denied)")

    def red_off(self):
        log.info("[leds] RED OFF")

    def yellow_on(self):
        log.info("[leds] YELLOW ON (processing)")

    def yellow_off(self):
        log.info("[leds] YELLOW OFF")

    def all_off(self):
        log.info("[leds] ALL OFF")


class GpioLEDs:
    mode = "gpio"

    def __init__(self, green_pin: int = 17, red_pin: int = 22, yellow_pin: int = 27):
        from gpiozero import LED
        self._green = LED(green_pin)
        self._red = LED(red_pin)
        self._yellow = LED(yellow_pin)
        self.all_off()

    def green_on(self):
        self.all_off()
        self._green.on()

    def green_off(self):
        self._green.off()

    def red_on(self):
        self.all_off()
        self._red.on()

    def red_off(self):
        self._red.off()

    def yellow_on(self):
        self.all_off()
        self._yellow.on()

    def yellow_off(self):
        self._yellow.off()

    def all_off(self):
        self._green.off()
        self._red.off()
        self._yellow.off()


def make_leds(settings) -> LEDController:
    if settings.led_mode == "gpio":
        try:
            return GpioLEDs(
                green_pin=settings.led_green_pin,
                red_pin=settings.led_red_pin,
                yellow_pin=settings.led_yellow_pin,
            )
        except Exception as e:
            log.error("GPIO LEDs failed, falling back to emulated: %s", e)
            return EmulatedLEDs()
    return EmulatedLEDs()