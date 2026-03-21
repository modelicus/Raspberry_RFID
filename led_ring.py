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

_BRAND = (145, 0, 72)
_IDLE_COLOR = (255, 255, 255)
_FADE_STEPS = 4      # steps for smooth color transitions
_FRAME_TIME = 0.02   # 50 FPS
_WAVE_WIDTH = 10     # LEDs in gradient wave — wider = smoother per-LED ramp


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
            self._pending_result = None  # "success" or "failure" — set while rfid_read animation plays
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
            if self.state == "rfid_read":
                self._pending_result = "success"
            else:
                self.state = "send_success"

    def trigger_send_failure(self):
        """Call if data send failed."""
        if not self.enabled:
            return
        with self._lock:
            if self.state == "rfid_read":
                self._pending_result = "failure"
            else:
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
                    result = self._pending_result
                    self._pending_result = None
                # Chain directly — no sleep gap between the two waves
                if result == "success":
                    self._animate_send_success()
                    with self._lock:
                        self.state = "idle"
                    continue
                elif result == "failure":
                    self._animate_send_failure()
                    with self._lock:
                        self.state = "idle"
                    continue
                else:
                    with self._lock:
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
        return (int(_IDLE_COLOR[0] * brightness), int(_IDLE_COLOR[1] * brightness), int(_IDLE_COLOR[2] * brightness))

    def _current_idle_color(self):
        # Range 0.25–1.0
        brightness = (math.sin(self._idle_phase) + 1) * 0.375 + 0.25
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
        brightness = (math.sin(self._idle_phase) + 1) * 0.375 + 0.25
        self._idle_phase += 0.04

        self.pixels.fill(self._idle_color(brightness))
        self.pixels.show()

    def _animate_rfid_read(self):
        """Sweep a gradient wave across the ring.
        At any frame the front LED is 0% green, with each trailing LED
        25% further along: 0% 25% 50% 75% 100%."""
        idle_color = self._current_idle_color()

        for head in range(LED_COUNT + _WAVE_WIDTH):
            with self._lock:
                if self.state != "rfid_read":
                    break

            for i in range(min(head + 1, LED_COUNT)):
                t = min(1.0, (head - i) / _WAVE_WIDTH)
                self.pixels[i] = self._lerp_color(idle_color, _BRAND, t)

            self.pixels.show()
            time.sleep(_FRAME_TIME)

    def _animate_send_success(self):
        """All LEDs simultaneously fade from brand to idle."""
        time.sleep(0.3)
        idle_color = self._current_idle_color()
        steps = 25
        for step in range(1, steps + 1):
            t = step / steps
            self.pixels.fill(self._lerp_color(_BRAND, idle_color, t))
            self.pixels.show()
            time.sleep(_FRAME_TIME)

    def _animate_send_failure(self):
        """Blink red 3 times from all-green, then fade back to idle."""
        black = (0, 0, 0)

        for _ in range(3):
            self.pixels.fill(_BRAND)
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
