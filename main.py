# main.py

import time
import signal
import sys
import RPi.GPIO as GPIO

from config import DEBOUNCE_SECONDS, UDP_PORT
from rfid_reader import RFIDReader
from udp_sender import UDPSender
from led_ring import LEDRing


# ============================================================
# Configuration Input
# ============================================================

def get_station_id() -> int:
    try:
        return int(input("Enter station ID: "))
    except ValueError:
        print("Invalid input. Using station ID = 0")
        return 0


def get_target_ip() -> str:
    ip = input("Enter target IP address: ").strip()
    return ip if ip else "127.0.0.1"


# ============================================================
# Station Controller
# ============================================================

class StationController:
    """
    Coordinates RFID reader, UDP sender, and LED system.
    Contains no animation logic and no timing logic.
    """

    def __init__(self, station_id: int, target_ip: str):
        self.station_id = station_id
        self.reader = RFIDReader(DEBOUNCE_SECONDS)
        self.sender = UDPSender(target_ip, UDP_PORT)
        self.led = LEDRing()
        self._running = False

    # ------------------------------
    # Lifecycle
    # ------------------------------

    def start(self):
        print("Station ready...")
        print(f"Sending UDP packets to {self.sender.target_ip}:{UDP_PORT}")

        self._running = True
        self._event_loop()

    def stop(self):
        print("Shutting down station...")

        self._running = False

        try:
            self.sender.close()
        finally:
            self.led.stop()
            GPIO.cleanup()

    # ------------------------------
    # Core Event Loop
    # ------------------------------

    def _event_loop(self):
        """
        Polls RFID reader continuously.
        LED animations are fully autonomous.
        """
        while self._running:
            uid = self.reader.read_uid()

            if uid:
                self._handle_scan(uid)

            # No animation timing here.
            # Small sleep to prevent CPU spin.
            time.sleep(0.005)

    # ------------------------------
    # Scan Handling
    # ------------------------------

    def _handle_scan(self, uid: str):
        print(f"Scanned UID: {uid}")

        try:
            self.sender.send_uid(self.station_id, uid)
            self.led.trigger_success()
        except Exception as e:
            print(f"Send error: {e}")
            self.led.trigger_error()


# ============================================================
# Entry Point
# ============================================================

def main():
    station_id = get_station_id()
    target_ip = get_target_ip()

    controller = StationController(station_id, target_ip)

    def shutdown_handler(signum, frame):
        controller.stop()
        sys.exit(0)

    # Handle Ctrl+C and system signals cleanly
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    controller.start()


if __name__ == "__main__":
    main()
