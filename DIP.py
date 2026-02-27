# DIP.py
# Reads a 4-position DIP switch to determine the station ID (0-15).
#
# Wiring: each switch connects the GPIO pin to GND (active-low).
# Internal pull-ups are enabled, so an open switch reads HIGH (1),
# a closed switch reads LOW (0).
#
# Pin mapping (BCM numbering):
#   DIP bit 0 (LSB) -> GPIO5  (Pin 29)
#   DIP bit 1       -> GPIO6  (Pin 31)
#   DIP bit 2       -> GPIO13 (Pin 33)
#   DIP bit 3 (MSB) -> GPIO19 (Pin 35)
#
# Station ID = bit3<<3 | bit2<<2 | bit1<<1 | bit0
# Example: switches 1 and 3 ON -> ID = 0b0101 = 5

import RPi.GPIO as GPIO

DIP_PINS = [5, 6, 13, 19]  # LSB to MSB


def setup():
    for pin in DIP_PINS:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def read_station_id() -> int:
    station_id = 0
    for bit, pin in enumerate(DIP_PINS):
        if GPIO.input(pin) == GPIO.LOW:  # switch ON (connected to GND)
            station_id |= (1 << bit)
    return station_id
