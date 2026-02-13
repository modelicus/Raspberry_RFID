import time
import socket
import json
import RPi.GPIO as GPIO
from mfrc522 import MFRC522

DEBOUNCE_SECONDS = 10
UDP_PORT = 5005


def get_station_id():
    try:
        station_id = int(input("Enter station ID: "))
        return station_id
    except ValueError:
        print("Invalid station ID. Using 0.")
        return 0


def get_target_ip():
    ip = input("Enter target IP address: ").strip()
    return ip


def main():
    station_id = get_station_id()
    target_ip = get_target_ip()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    reader = MFRC522()
    last_seen = {}

    print("RC522 ready. Waiting for RFID card...")
    print(f"Sending UDP packets to {target_ip}:{UDP_PORT}")

    try:
        while True:
            (status, _) = reader.MFRC522_Request(reader.PICC_REQIDL)

            if status == reader.MI_OK:
                (status, uid) = reader.MFRC522_Anticoll()

                if status == reader.MI_OK:
                    uid_str = "".join(f"{byte:02X}" for byte in uid)
                    now = time.time()

                    if uid_str in last_seen:
                        if now - last_seen[uid_str] < DEBOUNCE_SECONDS:
                            continue

                    last_seen[uid_str] = now

                    payload = {
                        "station_id": station_id,
                        "uid": uid_str,
                        "timestamp": int(now)
                    }

                    message = json.dumps(payload).encode("utf-8")

                    sock.sendto(message, (target_ip, UDP_PORT))

                    print(f"Sent: {payload}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        sock.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
