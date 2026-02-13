# main.py

import time
import RPi.GPIO as GPIO
from config import DEBOUNCE_SECONDS, UDP_PORT
from rfid_reader import RFIDReader
from udp_sender import UDPSender
from led_ring import LEDRing


def get_station_id():
    try:
        return int(input("Enter station ID: "))
    except ValueError:
        return 0


def get_target_ip():
    return input("Enter target IP address: ").strip()


def main():
    station_id = get_station_id()
    target_ip = get_target_ip()

    reader = RFIDReader(DEBOUNCE_SECONDS)
    sender = UDPSender(target_ip, UDP_PORT)
    led = LEDRing()

    print("Station ready...")

    try:
        while True:
            uid = reader.read_uid()

            if uid:
                print(f"Scanned UID: {uid}")

                try:
                    sender.send_uid(station_id, uid)
                    led.success_flash()
                except Exception as e:
                    print(f"Send error: {e}")
                    led.error_flash()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        sender.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
