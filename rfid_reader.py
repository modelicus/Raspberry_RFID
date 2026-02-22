import time
from mfrc522 import MFRC522


class RFIDReader:

    def __init__(self, debounce_seconds=10):

        self.reader = MFRC522()

        self.debounce_seconds = debounce_seconds

        self.last_seen = {}


    # -------------------------
    # Read UID (4 or 7 bytes)
    # -------------------------

    def read_uid(self):

        # Detect card

        (status, _) = self.reader.MFRC522_Request(
            self.reader.PICC_REQIDL
        )

        if status != self.reader.MI_OK:
            return None


        # Anticollision

        (status, uid) = self.reader.MFRC522_Anticoll()

        if status != self.reader.MI_OK:
            return None


        # Select tag
        # Required for long UID tags

        self.reader.MFRC522_SelectTag(uid)


        # Remove checksum byte

        uid_bytes = uid[:4]


        # Convert to HEX

        uid_str = "".join(
            f"{byte:02X}" for byte in uid_bytes
        )


        # Debounce

        now = time.time()

        if uid_str in self.last_seen:

            if now - self.last_seen[uid_str] < self.debounce_seconds:
                return None


        self.last_seen[uid_str] = now


        return uid_str
