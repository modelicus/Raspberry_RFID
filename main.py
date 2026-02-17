# main.py

import time
import RPi.GPIO as GPIO

from config import DEBOUNCE_SECONDS, UDP_PORT
from rfid_reader import RFIDReader
from udp_sender import UDPSender
from led_ring import LEDRing


# ----------------------------------------
# Configuration Prompts
# ----------------------------------------

def get_station_id():
    try:
        return int(input("Enter station ID: "))
    except ValueError:
        print("Invalid input. Using station ID = 0")
        return 0


def get_target_ip():
    ip = input("Enter target IP address: ").strip()
    if not ip:
        print("No IP entered. Defaulting to 127.0.0.1")
        ip = "127.0.0.1"
    return ip


# ----------------------------------------
# Core Runtime Logic
# ----------------------------------------

def handle_scan(uid, station_id, sender, led):
    """
    Handles a single RFID scan event.
    Responsible for:
    - Sending UID
    - Triggering LED animation
    """

    print(f"Scanned UID: {uid}")

    try:
        sender.send_uid(station_id, uid)
        led.success_animation()
    except Exception as e:
        print(f"Send error: {e}")
        led.error_flash()


def run_event_loop(reader, sender, led, station_id):
    """
    Main runtime loop.
    - Continuously checks for RFID
    - Updates idle LED animation
    """

    LOOP_DELAY = 0.02  # 50Hz loop

    while True:
        uid = reader.read_uid()

        if uid:
            handle_scan(uid, station_id, sender, led)
        else:
            led.update_idle()

        time.sleep(LOOP_DELAY)


# ----------------------------------------
# Entry Point
# ----------------------------------------

def main():
    station_id = get_station_id()
    target_ip = get_target_ip()

    reader = RFIDReader(DEBOUNCE_SECONDS)
    sender = UDPSender(target_ip, UDP_PORT)
    led = LEDRing()

    print("Station ready...")
    print(f"Sending UDP packets to {target_ip}:{UDP_PORT}")

    try:
        run_event_loop(reader, sender, led, station_id)

    except KeyboardInterrupt:
        print("\nShutting down...")

    finally:
        sender.close()
        led.clear()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
