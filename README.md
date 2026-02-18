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

2. Enable SPI
   ```
   sudo raspi-config
   ```
   ```
   Interface Options → SPI → Enable
   ```

3. Prepare folder for the project
   ```
   mkdir -p ~/apps/rfid_station
   cd ~/apps/rfid_station
   ```

4. Prepare virtual environment inside project folder
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Install all the necessary libraries
   ```
   pip install --upgrade pip
   pip install gpiozero
   pip install rpi_ws281x
   pip install spidev
   pip install mfrc522
   pip install requests
   pip3 install rpi_ws281x adafruit-circuitpython-neopixel
   python3 -m pip install --force-reinstall adafruit-blinka
   ```

6. Clone this repository
   ```
   git clone https://github.com/modelicus/Raspberry_RFID
   ```

7. Run the code
   ```
   sudo venv/bin/python Raspberry_RFID/main.py
   ```

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



