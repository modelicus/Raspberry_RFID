# led_ring.py

import time
try:
    from rpi_ws281x import PixelStrip, Color
except ImportError:
    print("rpi_ws281x not found. LED ring will not work.")
    PixelStrip = None
    Color = None

LED_COUNT = 12
LED_PIN = 10        # GPIO10 (MOSI)
LED_FREQ_HZ = 800000
LED_DMA = 10        # DMA channel (not critical in SPI mode)
LED_BRIGHTNESS = 50
LED_INVERT = False
LED_CHANNEL = 1     # SPI channel

class LEDRing:
    def __init__(self):
        self.enabled = PixelStrip is not None
        if not self.enabled:
            return

        try:
            self.strip = PixelStrip(
                LED_COUNT,
                LED_PIN,
                LED_FREQ_HZ,
                LED_DMA,
                LED_INVERT,
                LED_BRIGHTNESS,
                LED_CHANNEL
            )
            self.strip.begin()
        except Exception as e:
            print(f"Failed to initialize LED strip: {e}")
            self.enabled = False

    def success_flash(self):
        if not self.enabled:
            return
        self.set_color(Color(0, 100, 0))
        time.sleep(0.3)
        self.clear()

    def error_flash(self):
        if not self.enabled:
            return
        self.set_color(Color(100, 0, 0))
        time.sleep(0.3)
        self.clear()

    def set_color(self, color):
        if not self.enabled:
            return
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def clear(self):
        if not self.enabled:
            return
        self.set_color(Color(0, 0, 0))
