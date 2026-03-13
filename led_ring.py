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

_GREEN = (0, 180, 0)
_FADE_STEPS = 4     # steps for smooth color transitions
_FRAME_TIME = 0.02  # 50 FPS


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

    def trigger_rfid_read(self):
        """Call immediately on RFID scan, before sending data."""
        if not self.enabled:
            return
        with self._lock:
            self.state = "rfid_read"

    def trigger_send_success(self):
        """Call after data was sent successfully."""
        if not self.enabled:
            return
        with self._lock:
            self.state = "send_success"

    def trigger_send_failure(self):
        """Call if data send failed."""
        if not self.enabled:
            return
        with self._lock:
            self.state = "send_failure"

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

            elif current_state == "rfid_read":
                self._animate_rfid_read()
                with self._lock:
                    # Only advance to awaiting_send if send result hasn't arrived yet
                    if self.state == "rfid_read":
                        self.state = "awaiting_send"

            elif current_state == "awaiting_send":
                time.sleep(_FRAME_TIME)

            elif current_state == "send_success":
                self._animate_send_success()
                with self._lock:
                    self.state = "idle"

            elif current_state == "send_failure":
                self._animate_send_failure()
                with self._lock:
                    self.state = "idle"

            time.sleep(_FRAME_TIME)

    # ----------------------------------
    # Helpers
    # ----------------------------------

    def _idle_color(self, brightness):
        return (int(255 * brightness), int(80 * brightness), 0)

    def _current_idle_color(self):
        # Range 0.5–1.0 to stay above half brightness
        brightness = (math.sin(self._idle_phase) + 1) / 4 + 0.5
        return self._idle_color(brightness)

    def _lerp_color(self, a, b, t):
        return (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

    # ----------------------------------
    # Animations
    # ----------------------------------

    def _animate_idle(self):
        # 0.04 is 50% slower than original 0.08; brightness stays 50%–100%
        brightness = (math.sin(self._idle_phase) + 1) / 4 + 0.5
        self._idle_phase += 0.04

        self.pixels.fill(self._idle_color(brightness))
        self.pixels.show()

    def _animate_rfid_read(self):
        """Sweep LEDs 1→16, each fading smoothly from idle amber to green."""
        idle_color = self._current_idle_color()

        for i in range(LED_COUNT):
            # Allow early exit if send result already came in
            with self._lock:
                if self.state != "rfid_read":
                    break

            for step in range(1, _FADE_STEPS + 1):
                t = step / _FADE_STEPS
                self.pixels[i] = self._lerp_color(idle_color, _GREEN, t)
                self.pixels.show()
                time.sleep(_FRAME_TIME)

    def _animate_send_success(self):
        """Fade all LEDs from green back to idle amber simultaneously."""
        idle_color = self._current_idle_color()

        for step in range(1, _FADE_STEPS + 1):
            t = step / _FADE_STEPS
            self.pixels.fill(self._lerp_color(_GREEN, idle_color, t))
            self.pixels.show()
            time.sleep(_FRAME_TIME)

    def _animate_send_failure(self):
        """Blink red 3 times from all-green, then fade back to idle."""
        red = (180, 0, 0)
        black = (0, 0, 0)

        for _ in range(3):
            self.pixels.fill(red)
            self.pixels.show()
            time.sleep(0.3)
            self.pixels.fill(black)
            self.pixels.show()
            time.sleep(0.2)

        # Fade from black back to idle
        idle_color = self._current_idle_color()
        for step in range(1, _FADE_STEPS + 1):
            t = step / _FADE_STEPS
            self.pixels.fill(self._lerp_color(black, idle_color, t))
            self.pixels.show()
            time.sleep(_FRAME_TIME)

    def clear(self):
        self.pixels.fill((0, 0, 0))
        self.pixels.show()
