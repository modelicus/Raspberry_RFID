# time_sync.py
# Fetches current time from the backend and sets the system clock.
# Must run as root (sudo / systemd service) to set system time.

import os
import time
import requests

TIME_SYNC_RETRIES = 10
TIME_SYNC_RETRY_DELAY = 3  # seconds between retries


def sync_time_from_backend(base_url: str):
    url = f"{base_url}/api/time"
    for attempt in range(1, TIME_SYNC_RETRIES + 1):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            os.clock_settime(time.CLOCK_REALTIME, data["unix_ms"] / 1000.0)
            print(f"System time set from backend: {data['timestamp']}")
            return
        except Exception as e:
            print(f"Time sync attempt {attempt}/{TIME_SYNC_RETRIES} failed: {e}")
            if attempt < TIME_SYNC_RETRIES:
                time.sleep(TIME_SYNC_RETRY_DELAY)
    print("WARNING: Could not sync time from backend. Proceeding with system clock.")
