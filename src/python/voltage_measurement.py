#----------------------------------------
# Library Imports
#----------------------------------------

import time



#----------------------------------------
# trigger_arduino(ser)
#
# parameter:
#	- ser: the UART serial port object
#
# function description:
#	Sends an 'A' to the Arduino over the UART channel; this signal indicates
#	to the Arduino that the RaspberryPi is ready to receive a voltage
#	measurement over the UART channel (the Arduino is coded to send a value as
#	a result of this signal). 
#----------------------------------------

def trigger_arduino(ser):
    # Terminal logging
    print('Requesting value from Arduino')
    
    # Formatting instruction
    instruction = 'A'.encode('utf-8')
    
    # Writing instruction to the UART channel
    ser.write(instruction)
    
    # Time delay
    time.sleep(5)



#----------------------------------------
# read_from_UART(ser)
#
# parameter:
#	-ser: the UART serial port object
#
# returns: the value read from the UART channel.
#
# function description:
#	Voltage measurement data goes from the voltage module to the Arduino ADC. The
#	RaspberryPi receives the data from the ADC over a UART channel. This function
#	reads a value from the UART channel and returns it. 
#----------------------------------------

def read_from_UART(ser):
    # Terminal logging
    print('Reading from UART')
    
    # Read line, decode, and remove whitespace
    value = ser.readline().decode('utf-8').strip()
    print('value read: ', value)
    
    # Returning data if valid
    try:
        return float(value)
    except ValueError:
        print('Issue reading from UART: Invalid data received')
        print('Completed with warning\n')



#----------------------------------------
# apply_calibration_factor(raw_value, measured_voltages)
#
# parameters:
#	- raw_value: a single value (non-calibrated)
#	- measured_voltages: array to be filled with measured voltages
#
# function description:
#	This function takes in a raw value from the ADC and applies the calibration
#	factor, converting the voltage to its actual, accurate value. This
#	result is appended to the 'measured_voltages' array.
#
#----------------------------------------

def apply_calibration_factor(raw_value, measured_voltages):

    calibrated = process_voltage(raw_value)    
    measured_voltages.append(calibrated)
    print('Applied calibration: ', raw_value, ' --> ', calibrated)


def process_voltage(raw_value):
    if raw_value < 34.9497:
        return abs(0.4666*raw_value - 1.0444)
    elif raw_value > 211.6943:
        return abs(1.0097*raw_value - 115.93)
    else:
        return abs(0.456*raw_value - 1.3223)



#----------------------------------------
# close_UART_channel(ser)
#
# parameters:
#	- ser: the UART serial port object
#
# function description:
#	Closes the UART channel
#----------------------------------------

def close_UART_channel(ser):
    # Closing channel
    ser.close()
    
    # Terminal logging
    print('Closed UART channel')