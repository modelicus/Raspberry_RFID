# led_ring.py

import time
from rpi_ws281x import PixelStrip, Color
from config import LED_COUNT, LED_GPIO_PIN

class LEDRing:
    def __init__(self):
        self.strip = PixelStrip(
            LED_COUNT,
            LED_GPIO_PIN,
            800000,
            10,
            False,
            255,
            0
        )
        self.strip.begin()

    def success_flash(self):
        self.set_color(Color(0, 100, 0))
        time.sleep(0.3)
        self.clear()

    def error_flash(self):
        self.set_color(Color(100, 0, 0))
        time.sleep(0.3)
        self.clear()

    def set_color(self, color):
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def clear(self):
        self.set_color(Color(0, 0, 0))
