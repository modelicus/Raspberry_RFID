# rfid_reader.py

import time
from pirc522 import RFID

class RFIDReader:
    def __init__(self, debounce_seconds=10, bus=0, device=0):
        """
        Initialize RFID reader in polling mode (no IRQ), without setting GPIO mode.
        Debounce prevents repeated reads.
        """
        # Do NOT set GPIO mode here to avoid conflicts with other libraries
        self.reader = RFID(bus=bus, device=device, pin_irq=None, pin_mode=None)

        self.debounce_seconds = debounce_seconds
        self.last_seen = {}

    def read_uid(self):
        """
        Poll for an RFID tag and return the UID as uppercase hex string.
        Returns None if no tag is present or within debounce interval.
        Supports MIFARE Classic and Ultralight (7-byte) tags.
        """
        # Poll for tag presence
        error, tag_type = self.reader.request()
        if error:
            return None

        # Anti-collision to read UID
        error, uid = self.reader.anticoll()
        if error:
            return None

        # Handle Ultralight 7-byte UID
        if uid[0] == 0x88:  # incomplete UID
            error2, uid2 = self.reader.anticoll2()
            if error2:
                return None
            uid_bytes = uid[1:-1] + uid2[:-1]  # combine parts
        else:
            uid_bytes = uid[0:4]  # standard 4-byte UID

        # Convert bytes to uppercase hex string
        uid_str = "".join(f"{b:02X}" for b in uid_bytes)

        # Debounce logic
        now = time.time()
        if uid_str in self.last_seen and (now - self.last_seen[uid_str] < self.debounce_seconds):
            return None

        self.last_seen[uid_str] = now
        return uid_str

    def cleanup(self):
        """Clean up GPIO pins safely (calls stop_crypto if needed)"""
        self.reader.cleanup()
