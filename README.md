# V1 of Raspberry Pi software package for running RFID scanning stations and sending scan data to RFID_backend 

## Software

Tested on Raspberry Pi OS Lite 32bit running on Raspberry Pi 3B 1GB

1. After installing OS connect to internet and run these commands to update system:
   ```
   sudo apt update
   sudo apt full-upgrade -y
   sudo apt install -y python3-venv python3-pip git
   sudo reboot
   ```

2. Set a static IP address (required — no DHCP server on the local network):
   ```
   sudo nmcli con mod "netplan-eth0" ipv4.addresses 192.168.1.101/24 ipv4.method manual
   sudo nmcli con up "netplan-eth0"
   ```
   Replace `192.168.1.101` with the desired IP for this station. All stations and the backend server must be on the same `192.168.1.x` subnet.

3. Enable SPI
   ```
   sudo raspi-config
   ```
   ```
   Interface Options → SPI → Enable
   ```

4. Prepare folder for the project
   ```
   mkdir -p ~/apps/rfid_station
   cd ~/apps/rfid_station
   ```

5. Prepare virtual environment inside project folder
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

6. Install all the necessary libraries
   ```
   pip install --upgrade pip
   pip install RPi.GPIO
   pip install spidev
   pip install pi-rc522
   pip install rpi_ws281x
   pip install adafruit-circuitpython-neopixel
   pip install adafruit-blinka==8.43.0
   pip install requests
   ```

7. Clone this repository
   ```
   git clone https://github.com/modelicus/Raspberry_RFID
   ```

8. Set the backend IP in `Raspberry_RFID/config.py`:
   ```python
   TARGET_IP = "192.168.1.100"  # replace with your backend server IP
   ```

9. Run the code manually (for testing):
   ```
   sudo venv/bin/python Raspberry_RFID/main.py
   ```

10. Set up systemd service for autostart on boot:

   Create the service file:
   ```
   sudo nano /etc/systemd/system/rfid_station.service
   ```

   Paste the following (adjust the path if your username is not `pi`):
   ```ini
   [Unit]
   Description=RFID Scanning Station
   After=network-online.target
   Wants=network-online.target

   [Service]
   ExecStart=/home/pi/apps/rfid_station/venv/bin/python /home/pi/apps/rfid_station/Raspberry_RFID/main.py
   WorkingDirectory=/home/pi/apps/rfid_station
   Restart=always
   RestartSec=5
   User=root

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start the service:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable rfid_station.service
   sudo systemctl start rfid_station.service
   ```

   Check status / view logs:
   ```
   sudo systemctl status rfid_station.service
   sudo journalctl -u rfid_station.service -f
   ```

## On startup, the software automatically:
- Reads station ID from the 4-position DIP switch (no manual input needed)
- Syncs system time from `GET /api/time` on the backend (Raspberry Pi has no RTC battery)
- Sends a heartbeat `POST /api/heartbeat` to the backend every 30 seconds so the backend can detect offline stations

## Hardware

1. Connect RC522 module:
   ```
   SDA   ->  GPIO8 (CE0) – Pin 24
   SCK   ->  GPIO11 (SCLK) – Pin 23
   MOSI	 ->  GPIO10 – Pin 19
   MISO	 ->  GPIO9 – Pin 21
   IRQ   ->  Not connected
   GND   ->  GND – Pin 6
   RST   ->  GPIO25 – Pin 22
   3.3V  ->  3.3V – Pin 1
   ```

2. Connect WS2812B
   ```
   5V  -> 5V
   GND -> GND
   DI  -> GPIO18 - Pin 12
   ```

3. Connect 4-position DIP switch (each switch connects GPIO pin to GND; internal pull-ups used)
   ```
   Bit 0 (LSB) -> GPIO5  – Pin 29
   Bit 1       -> GPIO6  – Pin 31
   Bit 2       -> GPIO13 – Pin 33
   Bit 3 (MSB) -> GPIO19 – Pin 35
   GND         -> GND    – Pin 34 (or any GND)
   ```
   Station ID is the 4-bit binary value (0–15): switch ON = 1, switch OFF = 0.
   Example: switches 1 and 3 ON (bits 0 and 2) → ID = 5.


