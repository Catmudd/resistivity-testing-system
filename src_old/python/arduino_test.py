import time
import serial


ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=2)


while True:
    line = ser.readline().decode().strip()
    if line:
        voltages = [float(v) for v in line.split(',')]
        print(voltages)