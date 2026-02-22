# rfid_reader.py

import time
from pirc522 import RFID

class RFIDReader:
    def __init__(self, debounce_seconds=10):
        """
        Initialize the RFID reader with polling mode (no IRQ pin).
        """
        # Initialize RFID without IRQ
        self.reader = RFID(pin_irq=None)  # IRQ pin not connected
        self.debounce_seconds = debounce_seconds
        self.last_seen = {}

    def read_uid(self):
        """
        Poll for an RFID tag and return the UID as a hex string.
        Returns None if no tag is present or within debounce interval.
        Supports MIFARE Classic and Ultralight (7-byte) tags.
        """

        # Poll for tag presence
        error, tag_type = self.reader.request()
        if error:
            return None

        # Read UID
        error, uid = self.reader.anticoll()
        if error:
            return None

        # Handle Ultralight/7-byte tags
        if uid[0] == 0x88:
            # Incomplete UID, need second anticoll call
            error2, uid2 = self.reader.anticoll2()
            if error2:
                return None
            uid_bytes = uid[1:-1] + uid2[:-1]  # Combine first and second parts
        else:
            # Standard 4-byte UID
            uid_bytes = uid[0:4]

        # Convert UID bytes to uppercase hex string
        uid_str = "".join(f"{b:02X}" for b in uid_bytes)

        # Debounce logic
        now = time.time()
        if uid_str in self.last_seen and (now - self.last_seen[uid_str] < self.debounce_seconds):
            return None

        self.last_seen[uid_str] = now
        return uid_str
