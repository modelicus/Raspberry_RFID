import time
from pirc522 import RFID


class RFIDReader:

    def __init__(self, debounce_seconds=10):

        self.reader = RFID()

        self.debounce_seconds = debounce_seconds

        self.last_seen = {}


    def read_uid(self):

        # Wait for tag

        error, tag_type = self.reader.request()

        if error:
            return None


        # Read UID

        error, uid = self.reader.anticoll()

        if error:
            return None


        # Convert UID bytes

        uid_str = "".join(
            f"{byte:02X}" for byte in uid
        )


        # Debounce logic

        now = time.time()

        if uid_str in self.last_seen:

            if now - self.last_seen[uid_str] < self.debounce_seconds:
                return None


        self.last_seen[uid_str] = now


        return uid_str
