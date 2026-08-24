import serial
import time
try:
    ser = serial.Serial()
    ser.port = 'COM3'
    ser.baudrate = 115200
    ser.setDTR(False)
    ser.setRTS(False)
    ser.open()
    
    ser.write(b"CFG:ANIM:0\n")
    print("Sent CFG:ANIM:0 to reduce OLED power spike.")
    
    print("Listening on COM3 for 60 seconds (No DTR reset)...")
    end_time = time.time() + 60
    while time.time() < end_time:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(line)
        time.sleep(0.01)
    ser.close()
    print("Finished.")
except Exception as e:
    print(f"Error: {e}")
