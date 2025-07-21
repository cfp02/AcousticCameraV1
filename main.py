import serial
import numpy as np
import matplotlib.pyplot as plt

ser = serial.Serial('/dev/cu.usbmodem2101', 115200)  # Use correct port
ser.readline()

while True:
    try:
        line = ser.readline().decode().strip()
        if line:
            parts = line.split(',')
            if len(parts) == 2:
                micL, micR = int(parts[0]), int(parts[1])
                print(f"{micL},{micR}")
    except Exception as e:
        print("Error:", e)