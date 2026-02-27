# heartbeat.py
# Periodically POSTs a heartbeat to the backend so it can detect offline stations.

import threading
import requests
from datetime import datetime, timezone


class HeartbeatSender:
    def __init__(self, base_url: str, station_id: int, interval: int):
        self.endpoint = f"{base_url}/api/heartbeat"
        self.station_id = station_id
        self.interval = interval
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self.session.close()

    def _run(self):
        # wait(interval) blocks for `interval` seconds, then returns False.
        # Returns True immediately if stop() sets the event — clean exit.
        while not self._stop_event.wait(self.interval):
            self._send()

    def _send(self):
        payload = {
            "station": f"station_{self.station_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        try:
            response = self.session.post(self.endpoint, json=payload, timeout=3)
            response.raise_for_status()
        except Exception as e:
            print(f"Heartbeat failed: {e}")
