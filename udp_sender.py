# udp_sender.py

import socket
import json
import time

class UDPSender:
    def __init__(self, target_ip, port):
        self.target_ip = target_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_uid(self, station_id, uid):
        payload = {
            "station_id": station_id,
            "uid": uid,
            "timestamp": int(time.time())
        }

        message = json.dumps(payload).encode("utf-8")
        self.sock.sendto(message, (self.target_ip, self.port))

    def close(self):
        self.sock.close()
