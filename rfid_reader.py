# rfid_reader.py

import time
from pirc522 import RFID

class RFIDReader:
    def __init__(self, debounce_seconds=10, bus=0, device=0):
        # Polling mode only, no IRQ, no GPIO.setmode
        self.reader = RFID(bus=bus, device=device, pin_irq=None, pin_mode=None)
        self.debounce_seconds = debounce_seconds
        self.last_seen = {}

    def read_uid(self):
        # Poll for tag using REQALL (for Ultralight detection)
        error, _ = self.reader.request(self.reader.act_reqall)
        if error:
            return None

        # Use anticoll() to get first part of UID
        error, uid = self.reader.anticoll()
        if error:
            return None

        # Handle Ultralight (incomplete UID starts with 0x88)
        if uid[0] == 0x88:
            # perform second anticollision for remaining bytes
            error2, uid2 = self.reader.anticoll2()
            if error2:
                return None
            # Remove first and last BCC bytes from each part
            uid_bytes = uid[1:-1] + uid2[:-1]
        else:
            uid_bytes = uid[0:4]

        # Convert UID bytes to hex string
        uid_str = "".join(f"{b:02X}" for b in uid_bytes)

        # Debounce logic
        now = time.time()
        if uid_str in self.last_seen and (now - self.last_seen[uid_str] < self.debounce_seconds):
            return None

        self.last_seen[uid_str] = now
        return uid_str

    def cleanup(self):
        self.reader.cleanup()
