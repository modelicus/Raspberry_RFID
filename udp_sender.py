# udp_sender.py

import json
from datetime import datetime, timezone

import requests


class UDPSender:
    """
    Sends scan data to backend via HTTP POST /api/scan.
    """

    def __init__(self, target_ip: str, port: int):
        self.base_url = f"http://{target_ip}:{port}"
        self.endpoint = f"{self.base_url}/api/scan"

        # Optional: reuse TCP connection
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def send_uid(self, station_id: int, uid: str):
        """
        Sends a scan event to backend.
        Raises exception if request fails or returns non-2xx.
        """

        payload = self._build_payload(station_id, uid)

        response = self.session.post(
            self.endpoint,
            data=json.dumps(payload),
            timeout=3
        )

        # Raise exception on 4xx / 5xx
        response.raise_for_status()

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def _build_payload(self, station_id: int, uid: str) -> dict:
        """
        Builds JSON payload in backend-required format.
        """

        scanned_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "rfid": uid,
            "station": f"station_{station_id}",
            "scanned_at": scanned_at
        }

    # -------------------------------------------------

    def close(self):
        self.session.close()
