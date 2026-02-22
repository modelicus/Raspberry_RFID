# rfid_reader.py

import time
import RPi.GPIO as GPIO
from pirc522 import RFID


class RFIDReader:
    def __init__(self, debounce_seconds=10, bus=0, device=0):
        # Force BCM mode to avoid conflicts with other libraries
        GPIO.setmode(GPIO.BCM)

        # Initialize RFID reader with BCM pin mode
        self.reader = RFID(bus=bus, device=device, pin_mode=GPIO.BCM)

        self.debounce_seconds = debounce_seconds
        self.last_seen = {}

    def read_uid(self):
        """
        Reads a tag UID using read_id() and returns it as an uppercase hex string.
        Returns None if no tag is present or debounce blocks the read.
        Supports both MIFARE Classic and Ultralight 7-byte UIDs.
        """
        uid_bytes = self.reader.read_id()
        if uid_bytes is None:
            return None

        # Convert UID bytes to uppercase hex string
        uid_str = "".join(f"{b:02X}" for b in uid_bytes)

        # Debounce logic
        now = time.time()
        if uid_str in self.last_seen:
            if now - self.last_seen[uid_str] < self.debounce_seconds:
                return None

        self.last_seen[uid_str] = now
        return uid_str

    def cleanup(self):
        """Clean up GPIO pins safely"""
        GPIO.cleanup()
