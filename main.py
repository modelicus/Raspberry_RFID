# main.py

import time
import RPi.GPIO as GPIO
from config import DEBOUNCE_SECONDS, UDP_PORT
from rfid_reader import RFIDReader
from udp_sender import UDPSender
from led_ring import LEDRing



def get_station_id():
    """Prompt for station ID, fallback to 0 if invalid"""
    try:
        return int(input("Enter station ID: "))
    except ValueError:
        print("Invalid input. Using station ID = 0")
        return 0


def get_target_ip():
    """Prompt for target IP"""
    ip = input("Enter target IP address: ").strip()
    if not ip:
        print("No IP entered. Defaulting to 127.0.0.1")
        ip = "127.0.0.1"
    return ip


def main():
    # ---- Initialization ----
    station_id = get_station_id()
    target_ip = get_target_ip()

    reader = RFIDReader(DEBOUNCE_SECONDS)
    sender = UDPSender(target_ip, UDP_PORT)
    led = LEDRing()   # <-- Initialize LED ring

    print("Station ready...")
    print(f"Sending UDP packets to {target_ip}:{UDP_PORT}")

    try:
        while True:
            uid = reader.read_uid()

            if uid:
                print(f"Scanned UID: {uid}")

                try:
                    sender.send_uid(station_id, uid)
                    led.success_flash()   # <-- GREEN on success
                except Exception as e:
                    print(f"Send error: {e}")
                    led.error_flash()     # <-- RED on failure

            time.sleep(0.1)  # Small delay to reduce CPU usage

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        sender.close()
        led.clear()         # <-- Ensure LEDs turn off
        GPIO.cleanup()



if __name__ == "__main__":
    main()
