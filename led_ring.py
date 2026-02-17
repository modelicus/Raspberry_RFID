# led_ring.py

import time
import math

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
            pin = getattr(board, f"D{LED_GPIO_PIN}")

            self.pixels = neopixel.NeoPixel(
                pin,
                LED_COUNT,
                brightness=LED_BRIGHTNESS,
                auto_write=False
            )

            self._idle_phase = 0.0
            self._idle_speed = 0.08  # breathing speed

            self.clear()

        except Exception as e:
            print(f"Failed to initialize LED ring: {e}")
            self.enabled = False

    # -------------------------
    # IDLE BREATHING ORANGE
    # -------------------------
    def update_idle(self):
        if not self.enabled:
            return

        # Smooth sine wave brightness
        brightness = (math.sin(self._idle_phase) + 1) / 2  # 0–1
        self._idle_phase += self._idle_speed

        # Orange base (R high, G medium)
        r = int(255 * brightness)
        g = int(80 * brightness)
        b = 0

        self.pixels.fill((r, g, b))
        self.pixels.show()

    # -------------------------
    # SUCCESS ANIMATION
    # -------------------------
    def success_animation(self):
        if not self.enabled:
            return

        green = (0, 180, 0)
        orange = (180, 60, 0)

        # Sweep green forward
        for i in range(LED_COUNT):
            self.pixels[i] = green
            self.pixels.show()
            time.sleep(0.02)

        # Return to orange sweep
        for i in range(LED_COUNT):
            self.pixels[i] = orange
            self.pixels.show()
            time.sleep(0.02)

    # -------------------------
    # ERROR FLASH
    # -------------------------
    def error_flash(self):
        if not self.enabled:
            return
        self.pixels.fill((180, 0, 0))
        self.pixels.show()
        time.sleep(0.3)
        self.clear()

    def clear(self):
        if not self.enabled:
            return
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
