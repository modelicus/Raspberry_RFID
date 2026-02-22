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


        # Anti-collision

        (status, uid) = self.reader.MFRC522_Anticoll()

        if status != self.reader.MI_OK:
            return None


        # uid example:
        # [0x88, 0x04, 0x13, 0x25, 0xBA]
        #
        # 0x88 = Cascade Tag
        # Means UID continues


        uid_bytes = uid[:4]


        # Remove cascade byte if present

        if uid_bytes[0] == 0x88:

            uid_bytes = uid_bytes[1:]


            # Select first cascade level

            self.reader.MFRC522_SelectTag(uid)


            # Read second cascade level

            (status2, uid2) = self.reader.MFRC522_Anticoll()

            if status2 != self.reader.MI_OK:
                return None


            uid_bytes += uid2[:4]


        # Convert to HEX string

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
