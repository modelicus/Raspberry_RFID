# led_ring.py

import time
import math
import threading

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

            # Animation state
            self.state = "idle"
            self._idle_phase = 0.0
            self._lock = threading.Lock()
            self._running = True

            # Start animation thread
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

        except Exception as e:
            print(f"Failed to initialize LED ring: {e}")
            self.enabled = False

    # ----------------------------------
    # Public API
    # ----------------------------------

    def trigger_success(self):
        if not self.enabled:
            return
        with self._lock:
            self.state = "success"

    def trigger_error(self):
        if not self.enabled:
            return
        with self._lock:
            self.state = "error"

    def stop(self):
        if not self.enabled:
            return
        self._running = False
        self._thread.join()
        self.clear()

    # ----------------------------------
    # Internal Animation Engine
    # ----------------------------------

    def _run(self):
        while self._running:
            with self._lock:
                current_state = self.state

            if current_state == "idle":
                self._animate_idle()

            elif current_state == "success":
                self._animate_success()
                with self._lock:
                    self.state = "idle"

            elif current_state == "error":
                self._animate_error()
                with self._lock:
                    self.state = "idle"

            time.sleep(0.02)  # 50 FPS base timing

    # ----------------------------------
    # Animations
    # ----------------------------------

    def _animate_idle(self):
        brightness = (math.sin(self._idle_phase) + 1) / 2
        self._idle_phase += 0.08

        r = int(255 * brightness)
        g = int(80 * brightness)
        b = 0

        self.pixels.fill((r, g, b))
        self.pixels.show()

    def _animate_success(self):
        green = (0, 180, 0)
        orange = (180, 60, 0)

        # Sweep green
        for i in range(LED_COUNT):
            self.pixels[i] = green
            self.pixels.show()
            time.sleep(0.02)

        # Return to orange
        for i in range(LED_COUNT):
            self.pixels[i] = orange
            self.pixels.show()
            time.sleep(0.02)

    def _animate_error(self):
        self.pixels.fill((180, 0, 0))
        self.pixels.show()
        time.sleep(0.3)

    def clear(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
