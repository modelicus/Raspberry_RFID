import time
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

DEBOUNCE_SECONDS = 10

def main():
    reader = MFRC522()
    last_seen = {}
    
    print("RC522 ready. Waiting for RFID card...")

    try:
        while True:
            (status, tag_type) = reader.MFRC522_Request(reader.PICC_REQIDL)

            if status == reader.MI_OK:
                (status, uid) = reader.MFRC522_Anticoll()

                if status == reader.MI_OK:
                    uid_str = "".join(f"{byte:02X}" for byte in uid)

                    now = time.time()

                    # Debounce logic
                    if uid_str in last_seen:
                        if now - last_seen[uid_str] < DEBOUNCE_SECONDS:
                            continue

                    last_seen[uid_str] = now

                    print("Card detected!")
                    print(f"UID: {uid_str}")
                    print("-" * 30)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
