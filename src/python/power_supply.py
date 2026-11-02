#----------------------------------------
# Library Imports
#----------------------------------------

import pyvisa
import time
import subprocess

import troubleshoot



#----------------------------------------
# ping_LAN()
#
# function description:
#	Calls a bash script to handle LAN pinging. 
#----------------------------------------

def ping_LAN():    
    script_path = '../scripts/ping.sh'
    
    try:
        subprocess.run(['chmod', '+x', script_path], capture_output=True, text=True, check=True)
        print('Successfully pinged LAN')
    except subprocess.CalledProcessError as e:
        print('An error occurred while attempting to ping LAN')
    except FileNotFoundError:
        print('The ping bash script was not located at the expected location')



#----------------------------------------
# configure_ethernet(power_supply)
#
# parameter:
#	- power_supply: the power supply PyVISA global variable
#
# function description:
#	configures the ethernet connection between the RaspberryPi and the
#	power supply and puts the power supply in remote operating mode. 
#----------------------------------------

def configure_ethernet(power_supply):
    # Configuration
    power_supply.timeout = 10000
    power_supply.write_termination = '\n'
    power_supply.read_termination = '\n'
    print('IDN ', power_supply.query('*IDN?').strip())
    power_supply.write('SYST:REM')
    time.sleep(2)
    
    # Terminal logging
    print('Configured ethernet')
    


#----------------------------------------
# startup(power_supply)
#
# paramter:
#	- power_supply: the power supply PyVISA global variable 
#
# function description:
#	takes care of power supply startup tasks:
#		- sets frequency to 60Hz
#		- ensures dimmer setting is off
#----------------------------------------

def startup(power_supply):
 
    # Setting frequency
    power_supply.write('SOUR:FREQ 60')
    
    # Check dimmer setting
    power_supply.write('SOUR:DIMM:STAT OFF') # THIS LINE needs to be checked still
    
    # Terminal logging
    print('Power supply startup settings set')
    
    
    
#----------------------------------------
# set_voltage(power_supply, voltage)
#
# parameters:
#	- power_supply: the power supply PyVISA global variable
#	- voltage: the voltage (in Volts) to be set
#
# function description:
#	Sets the power supply voltage amount to 'v' Volts.
#
#	Note: this function does not turn the output channel on; it
#		  just sets the voltage level. 
#----------------------------------------

def set_voltage(power_supply, voltage):
    # Setting up the instruction string to be sent from the RaspberryPi to the power supply
    instruction = 'SOUR:VOLT ' + str(voltage)
    
    # Sending the instruction string over ethernet
    power_supply.write(instruction)
    
    # Terminal logging
    print('Voltage set to ', voltage, 'V')



#----------------------------------------
# channel_on(power_supply)
#
# parameter:
#	- power_supply: the power supply PyVISA global variable
#
# function description:
#	Turns the power supply voltage channel on; if a voltage has been set
#	with the set_voltage() function, that voltage will be applied. 
#----------------------------------------

def channel_on(power_supply):
    power_supply.write('OUTP ON')
    
    print('Power supply channel ON')



#----------------------------------------
# channel_off(power_supply)
#
# parameters:
#	- power_supply: the power supply PyVISA global variable
#
# function description:
#	Turns the power supply voltage channel off. 
#----------------------------------------

def channel_off(power_supply):
    power_supply.write('OUTP OFF')
    
    print('Power supply channel OFF\n')



#----------------------------------------
# measure_current(power_supply, measured_currents)
#
# parameters:
#	- power_supply: the power supply PyVISA global variable
#	- measured_currents: the array which stores the measured currents (this function fills it with values)
#
# function description:
#	Takes a current measurement and appends the measured value to the
#	'measured_currents' array. Note that current values are appended to the
#	array in order (the order of the applied test voltages), so measured results
#	in the array correspond to the test voltage in the matching index. 
#----------------------------------------

def measure_current(power_supply, measured_currents):
    # Querying the power supply for a current value
    current = power_supply.query('MEAS:CURR?')
    print('debug display: ', current)
    
    # Getting result as a float
    current = float(current)*1000
    
    # Appending result to the 'measured_currents' array
    measured_currents.append(current)
    
    # Terminal logging
    print('Measured current ', current, ' mA')



#----------------------------------------
# lead_connection_test()
#
# function description:
#	This function runs a low-voltage test and checks for expected
#	current readings. By measuring currents in the expected range
#	for the applied low voltage, it is likely that the test leads
#	are connected properly (because otherwise the expected current
#	results would not be obtained). This is a small additional safety
#	check for the program.
#
#   Test passes if current is within 30% (above or below) the expected value
#	for the applied voltage. 
#----------------------------------------

def lead_connection_test(power_supply):
    # Initial result setting
    pass_test = False
    
    # Setting voltage to 10 Volts
    instruction = 'SOUR:VOLT ' + str(10)
    power_supply.write(instruction)
    
    # Turning on channel
    power_supply.write('OUTP ON')
    time.sleep(2)
    
    # Taking a current measurement
    current = power_supply.query('MEAS:CURR?')
    current = float(current)*1000
    print('Current (mA) measured for the test is: ', current)
    
    # Turning off channel
    power_supply.write('OUTP OFF')
    
    # Checking for open circuit case
    if current >= 0.00005:
        pass_test = True
        print('Low-voltage lead connection test PASSED')
    
    # Running troubleshoot function if test fails
    if pass_test == False:
        print('Low-voltage lead connection test ***FAILED***')
        print('Running troubleshoot\n')
        troubleshoot.lead_connection_issue()
    
    
