import time
import serial
import pyvisa
import power_supply
import voltage_measurement
import csv

# import matplotlib.pyplot as plt
# import numpy as np


# Device Configs
bk = pyvisa.ResourceManager('@py').open_resource('TCPIP::192.168.1.10::5025::SOCKET')
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=2)

cal_limit=151
#cal_limit = 151 # test voltages up to this number - 1
adc_val = [] # to be filled
# test_voltages = []
# 
# for i in range(cal_limit):
#     test_voltages.append(i)


# Device Setup
power_supply.ping_LAN()
power_supply.configure_ethernet(bk)
power_supply.startup(bk)


# plt.ion()
# fig, ax = plt.subplots()
# line, = ax.plot(test_voltages, adc_val)


# Test Loop (get calibration data for voltages from 0 - 150 Volts in 1-Volt steps)
for i in range(cal_limit):
    # Set voltage
    power_supply.set_voltage(bk, i)
    power_supply.channel_on(bk)
    time.sleep(1.5)
    
    # Read
    voltage_measurement.trigger_arduino(ser)
    adc_val.append(voltage_measurement.read_from_UART(ser))
    print('(', i, ' Volts   ,   ', adc_val[i], ')')
    
    # Plot
#     line.set_data(test_voltages, adc_val)
#     ax.relim()
#     ax.autoscale_view()
#     fig.canvas.draw()
#     fig.canvas.flush_events()
#     plt.pause(0.01)
    
    # Reset
    power_supply.channel_off(bk)
    time.sleep(1)
    
     
# Build Result Table   
result_table = []
for i in range(cal_limit):
    row = []
    row.append(i)
    row.append(adc_val[i])
    result_table.append(row)
    

# Generate CSV
with open('./cal_results.csv', mode='w', newline='') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerows(result_table)
    
    
