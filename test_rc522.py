import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

def main():
    reader = SimpleMFRC522()
    print("RC522 ready. Waiting for RFID card...")

    try:
        while True:
            uid, text = reader.read()
            print(f"Card detected!")
            print(f"UID: {uid}")
            print(f"Text: {text.strip()}")
            print("-" * 30)

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
