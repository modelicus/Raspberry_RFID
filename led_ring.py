# led_ring.py

import time

try:
    import board
    import neopixel
except ImportError:
    print("neopixel library not found. LED ring will not work.")
    neopixel = None

from config import LED_COUNT, LED_GPIO_PIN, LED_BRIGHTNESS


class LEDRing:
    def __init__(self):
        self.enabled = neopixel is not None
        if not self.enabled:
            return

        try:
            # Convert GPIO number to board pin dynamically
            pin = getattr(board, f"D{LED_GPIO_PIN}")

            self.pixels = neopixel.NeoPixel(
                pin,
                LED_COUNT,
                brightness=LED_BRIGHTNESS,
                auto_write=False
            )

            self.clear()

        except Exception as e:
            print(f"Failed to initialize LED ring: {e}")
            self.enabled = False

    def success_flash(self):
        if not self.enabled:
            return
        self.set_color((0, 150, 0))
        time.sleep(0.3)
        self.clear()

    def error_flash(self):
        if not self.enabled:
            return
        self.set_color((150, 0, 0))
        time.sleep(0.3)
        self.clear()

    def set_color(self, color):
        if not self.enabled:
            return
        self.pixels.fill(color)
        self.pixels.show()

    def clear(self):
        if not self.enabled:
            return
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
