import serial
import time
import sys

try:
    ser = serial.Serial('COM3', 115200, timeout=1)
    print("Listening on COM3 for 25 seconds...")
    end_time = time.time() + 25
    while time.time() < end_time:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
        time.sleep(0.01)
    ser.close()
    print("Finished listening.")
except Exception as e:
    print(f"Error: {e}")
