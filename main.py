# main.py

import time
import signal
import sys
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from config import DEBOUNCE_SECONDS, UDP_PORT, TARGET_IP, HEARTBEAT_INTERVAL
from rfid_reader import RFIDReader
from udp_sender import UDPSender
from led_ring import LEDRing
from time_sync import sync_time_from_backend
from heartbeat import HeartbeatSender
import DIP


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
        self.heartbeat = HeartbeatSender(f"http://{target_ip}:{UDP_PORT}", station_id, HEARTBEAT_INTERVAL)
        self._running = False

    # ------------------------------
    # Lifecycle
    # ------------------------------

    def start(self):
        print("Station ready...")
        print(f"Sending HTTP requests to {self.sender.endpoint}")

        self.heartbeat.start()
        self._running = True
        self._event_loop()

    def stop(self):
        print("Shutting down station...")

        self._running = False

        try:
            self.sender.close()
            self.heartbeat.stop()
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
    DIP.setup()
    station_id = DIP.read_station_id()
    print(f"Station ID from DIP switch: {station_id}")

    sync_time_from_backend(f"http://{TARGET_IP}:{UDP_PORT}")

    controller = StationController(station_id, TARGET_IP)

    def shutdown_handler(signum, frame):
        controller.stop()
        sys.exit(0)

    # Handle Ctrl+C and system signals cleanly
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    controller.start()


if __name__ == "__main__":
    main()
