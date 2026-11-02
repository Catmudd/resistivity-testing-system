#----------------------------------------
# Library & Code Imports
#----------------------------------------

# Code imports (written by capstone team) --- functions organized into the following modules:
import calculations
import power_supply
import report_generation
import voltage_measurement
import troubleshoot

# Library imports
import time
import serial
import pyvisa


#----------------------------------------
# Variables
#----------------------------------------

# Test parameters

test_voltages = [50, 100, 150, 200, 250, 200, 150, 100, 50]
#test_voltages = [5, 10, 15, 20, 25, 20, 15, 10, 5]

retest_threshold = 5 # RSD% exceeding this amount (as a percent) requires a re-test
retest_limit = 3 # the program will not re-test more than this many times

# Values to be measured
measured_voltages = []
measured_currents = []

# Values to be calculated
resistance = []
resistivity = [] #redundant array, BPA worksheet only need a single summarized value
avg_resistivity = 0.0
avg_res = 0.0
std_dev = 0.0
rsd_pct = 0.0 # re-run if > 4%
pair_diffs = []
trial_id = []
fail_id = []


# Test cell geometry factor
cell_geometry_factor = 0.33 # accounts for cross-section area and cell length

# Input parameters
tester_name = ''
sample_id = ''

date = None
test_start_time = None

# Power supply
while True:
    try:   
        bk = pyvisa.ResourceManager('@py').open_resource('TCPIP::192.168.1.10::5025::SOCKET')
        break
    except Exception as e:
        troubleshoot.ethernet_issue()

# UART channel
# ser = serial.Serial('/dev/serial0', 9600, timeout=1)


# ------------------- troubleshooting

try:
    ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=2)
except Exception as e:
    print(e)


# ------------------------------------




# Report generation
results_file_type = 'csv' # default to csv
usb_drive_specifier = ''





#----------------------------------------
# Test Sequence
#----------------------------------------

def run_test(name, s_id, file_type, current_date, start_time):    
    #Storing user-inputted values as variables in the scope of 'main.py'
    tester_name = name
    sample_id = s_id
    results_file_type = file_type
    date = current_date
    test_start_time = start_time
    
    # Terminal logging
    print('--------------------')
    print('STARTING TEST SEQUENCE')
    print('--------------------\n')
    
    # Startup / configuration tasks
    power_supply.ping_LAN()
    power_supply.configure_ethernet(bk)
    power_supply.startup(bk)
    usb_drive_specifier = report_generation.check_for_connected_USB()
    power_supply.lead_connection_test(bk)
    
    # Test loop
    
    # Result Table (currently just a header row --- to be filled with data)
    FULL_TABLE = [
        ["V Applied", "V Measured", "Current (mA)", "Resistance", "Trial_ID", "Pass_ID"],  # Row 0: headers
     ]
    
    cycles_completed = 1
    test_complete = False # setting test_complete to False initially

    
    while not test_complete:
        
        # Emptying the arrays for the next cycle
        while len(measured_voltages) > 0:
            measured_currents.pop()
            measured_voltages.pop()
            resistance.pop()
            resistivity.pop()
        
        while len(pair_diffs) > 0:
            pair_diffs.pop()
        
        # Clearing stat values for next cycle
        avg_resistivity = 0.0
        avg_res = 0.0
        std_dev = 0.0
        rsd_pct = 0.0
    
        
        # Looping through the set of applied voltages
        for i in range(len(test_voltages)):
            
            
            
            #### Troubleshoot code
            
            print('\n')
            print('Power supply error code: ')
            print(bk.query("SYST:ERR?"))
            print('\n')
            
            
            #####
            
            
            
            
            
            # Setting and applying voltage
            power_supply.set_voltage(bk, test_voltages[i])
            power_supply.channel_on(bk)
            time.sleep(1.5)
            
            # Current measurement
            power_supply.measure_current(bk, measured_currents)
            
            # Voltage measurement
            voltage_measurement.trigger_arduino(ser)
            voltage_in = voltage_measurement.read_from_UART(ser)
            voltage_measurement.apply_calibration_factor(voltage_in, measured_voltages)
            
            # Get ready for next cycle
            power_supply.channel_off(bk)
            time.sleep(1)
    
        
        # Performing calculations
        calculations.calculate_resistance(measured_voltages, measured_currents, resistance)
        calculations.calculate_resistivity(resistance, resistivity, cell_geometry_factor)
        avg_res = calculations.calculate_average_resistance(resistance, avg_res)
        std_dev = calculations.calculate_standard_deviation(resistance, avg_res, std_dev)
        rsd_pct = calculations.calculate_percent_RSD(avg_res, std_dev, rsd_pct)
        calculations.calculate_rel_diff_percents(resistance, pair_diffs)
        
        
        # Building report table (CSV 1)
        
        # -- build table for the current cycle
        ACTIVE_TABLE = report_generation.populate_active_table(test_voltages, measured_voltages, measured_currents, resistance, rsd_pct, retest_threshold, cycles_completed)
        
        # -- append the current-cycle table to the full-test (accumulative) table
        FULL_TABLE = report_generation.append_active_to_full_table(ACTIVE_TABLE, FULL_TABLE)
        9.5054656	
        # Terminal logging for monitoring
        for row in FULL_TABLE:
            print(*row, sep='\t\t')
                
        # Checking data collection completion
        test_complete = report_generation.check_test_complete(cycles_completed, retest_limit, FULL_TABLE)
        
        # Incrementing cycles completed counter
        cycles_completed = cycles_completed + 1
        
        # [end of loop]
        
    
    # Building stat table (CSV 2)
    STAT_TABLE = report_generation.build_stat_table(FULL_TABLE, tester_name, sample_id, date, test_start_time)
    print(STAT_TABLE)
    
    
    # Report generation and copy over
    
    # -- Create results directory
    directory = report_generation.create_directory(date, test_start_time, sample_id)
    
    # -- Create requested report types
    if results_file_type == 'pdf':
        report_generation.generate_PDF(FULL_TABLE, STAT_TABLE, directory, tester_name, sample_id, date, test_start_time)
    elif results_file_type == 'both':
        report_generation.generate_PDF(FULL_TABLE, STAT_TABLE, directory, tester_name, sample_id, date, test_start_time)
        report_generation.generate_CSV1(FULL_TABLE, directory, sample_id)
        report_generation.generate_CSV2(STAT_TABLE, directory, sample_id)
    else:
        report_generation.generate_CSV1(FULL_TABLE, directory, sample_id)
        report_generation.generate_CSV2(STAT_TABLE, directory, sample_id)
    
    # -- Copying to USB drive
    report_generation.copy_to_USB(directory, usb_drive_specifier)
        
    
    
    # Shutdown tasks
    voltage_measurement.close_UART_channel(ser)
    
    # -- ensure power supply finishes at 0 Volt setting
    power_supply.set_voltage(bk, 0)
    power_supply.channel_off(bk)
    time.sleep(1.5)
    
    
    # Terminal logging
    print('--------------------')
    print('TEST SEQUENCE COMPLETED')
    print('--------------------\n')
    
    return 0
