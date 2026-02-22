import time
from mfrc522 import MFRC522


class RFIDReader:

    def __init__(self, debounce_seconds=10):

        self.reader = MFRC522()

        self.debounce_seconds = debounce_seconds

        self.last_seen = {}


    # -------------------------
    # Read FULL UID
    # -------------------------

    def read_uid(self):

        # Detect card

        (status, _) = self.reader.MFRC522_Request(
            self.reader.PICC_REQIDL
        )

        if status != self.reader.MI_OK:
            return None


        # Full anticollision + select
        # This returns entire UID

        (status, uid) = self.reader.MFRC522_SelectTagSN()

        if status != self.reader.MI_OK:
            return None


        # Convert to HEX string
        # Example:
        # 041325BABD370289

        uid_str = "".join(
            f"{byte:02X}" for byte in uid
        )


        # Debounce

        now = time.time()

        if uid_str in self.last_seen:

            if now - self.last_seen[uid_str] < self.debounce_seconds:

                return None


        self.last_seen[uid_str] = now


        return uid_str
