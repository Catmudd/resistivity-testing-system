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

test_voltage_levels = [50, 100, 150, 200, 250] # Keeping static for now, will need to be made dynamic.

RETEST_THRESHOLD = 5 # RSD% exceeding this amount (as a percent) requires a re-test
RETEST_LIMIT = 3 # the program will not re-test more than this many times

#----------------------------------------
# # Values to be measured (changed from declarations to checklist)
#----------------------------------------
#   voltages
#   currents

#----------------------------------------
# # Values to be calculated (changed from declarations to checklist)
#----------------------------------------
#   resistances
#   resistivities (redundant array, BPA worksheet only need a single summarized value)
#   average resistivity
#   average resistance
#   standard deviation
#   RSD percent (defined as: 100 * (standard deviation / average)
#       re-run if RSD > 4%
#   relative min/max resistances


# Test cell geometry factor
CELL_GEOMETRY_FACTOR = 0.33 # accounts for cross-section area and cell length

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

# Check if v is approximately n within some epsilon.
def is_v_approx_n(v, n, epsilon):
    return v > n - epsilon and v < n + epsilon

# Ensure power supply finishes at 0 Volt setting.
def power_supply_safe_finish(bk):
    power_supply.set_voltage(bk, 0)
    power_supply.channel_off(bk)
    time.sleep(1.5)

# Take test sample.
# measured_currents and measured_voltages inside this function are LOCALLY SCOPED,
# and do not refer to the globally-scoped measured_currents and measured_voltages.
# TODO: Eliminate globally-scoped variants.
# Returns true iff last VOLT_WAIT_PASS_NUM tests succeeded.
def take_sample(bk: pyvisa.Resource, ser: serial.Serial, test_voltage: int, measured_currents: dict[int:list[float]], measured_voltages: dict[int:list[float]]) -> bool:

    # ================================================================
    # PART 0: Old Code for Reference
    # ================================================================

    # # Troubleshoot code
    # print('\n')
    # print('Power supply error code: ')
    # print(bk.query("SYST:ERR?"))
    # print('\n')
    
    # # Setting and applying voltage
    # power_supply.set_voltage(bk, test_voltage)
    # power_supply.channel_on(bk)
    # time.sleep(1.5)
    
    # # Current measurement
    # power_supply.measure_current(bk, measured_currents)
    
    # # Voltage measurement
    # voltage_measurement.trigger_arduino(ser)
    # voltage_in = voltage_measurement.read_from_UART(ser)
    # voltage_measurement.apply_calibration_factor(voltage_in, measured_voltages)
    
    # # Get ready for next cycle
    # power_supply.channel_off(bk)
    # time.sleep(1)

    VOLT_WAIT_PASS_NUM: float = 4
    VOLT_WAIT_SEC: float = 0.1
    VOLT_WAIT_MAX_SAMPLES: float = 20
    VOLT_WAIT_DEVIANCE: float = 1
    VOLT_WAIT_ERROR: float = 20

    read_voltages = []

    # ================================================================
    # PART 1: Wait for voltage read by Arduino to stablize
    # If it never does, or an error occurs, raise it and 
    # reset power supply.
    # ================================================================

    power_supply.set_voltage(bk, test_voltage)
    power_supply.channel_on(bk)

    volt_error: bool = False # True iff any voltage not equal test_voltage, + or - VOLT_WAIT_ERROR.
    volt_pass: bool = False # True iff last VOLT_WAIT_PASS_NUM voltages equal test_voltage, + or - VOLT_WAIT_DEVIANCE.

    for i in range(VOLT_WAIT_MAX_SAMPLES):

        time.sleep(VOLT_WAIT_SEC)

        # Read voltage and stick it into buffer head.
        voltage_measurement.trigger_arduino(ser)
        raw_voltage: float = voltage_measurement.read_from_UART(ser)
        processed_voltage = voltage_measurement.process_voltage(raw_voltage)
        read_voltages.insert(0, processed_voltage)

        # Catch unnacceptable voltages.
        if (not is_v_approx_n(read_voltages[0], test_voltage, VOLT_WAIT_ERROR)):
            volt_error = True
            break

        # Wait until has at least taken VOLT_WAIT_PASS_NUM samples
        # to actually check samples and see if they're all within bounds.
        if (i < VOLT_WAIT_PASS_NUM):
            continue

        # If most recent VOLT_WAIT_PASS_NUM sampkes fall within max deviance, 
        # great! We can break. Otherwise, keep re-checking until timeout.
        if all(is_v_approx_n(voltage, test_voltage, VOLT_WAIT_DEVIANCE) for voltage in read_voltages[0:VOLT_WAIT_PASS_NUM]):
            volt_pass = True
            break
    
    # ================================================================
    # PART 2: Append data to lists.
    # ================================================================

    if (volt_error):
        power_supply.channel_off(bk)
        raise Exception(f'Voltage exceeded safety bounds ({read_voltages[0]}).')

    power_supply.measure_current(bk, test_voltage, measured_currents)
    power_supply.channel_off(bk)
    time.sleep(VOLT_WAIT_SEC)

    if test_voltage not in measured_voltages:
        measured_voltages[test_voltage] = []
    measured_voltages[test_voltage].append(read_voltages[0])
    return volt_pass

#----------------------------------------
# Test Sequence
#----------------------------------------

def run_test(name: str, s_id: str, file_type: str, current_date: str, start_time: str) -> int:    
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
    full_table = [
        ["V Applied", "V Measured", "Currents (mA)", "Resistances (ohms)", "Trial_ID", "Pass_ID"],  # Row 0: headers
     ]
    
    cycles_completed = 0
    test_complete = False # setting test_complete to False initially

    measured_voltages = dict()
    measured_currents = dict()

    # Ascending and then descending behavior - should work regardless of which values are present.
    test_voltages = sorted(test_voltage_levels) + sorted(test_voltage_levels, reverse=True)
    
    while not test_complete:
        
        # Looping through the set of applied voltages.
        # Try taking a sample, but if something excepts,
        # safely shut off hardware and re-emit the error.
        for test_voltage in test_voltages:

            if test_voltage not in measured_voltages:
                measured_voltages[test_voltage] = []
            if test_voltage not in measured_currents:
                measured_currents[test_voltage] = []
            
            try: 
                if not take_sample(bk, ser, test_voltage, measured_currents, measured_voltages):
                    print(f"Voltage {test_voltage} failed. Continuing...")
            except:
                voltage_measurement.close_UART_channel(ser)
                power_supply_safe_finish(bk)
                raise

        # Abandon testing if no measurements taken.
        if (not measured_currents) or (not measured_voltages):
            print("ERROR: Missing voltage/current measurements. Aborting tests...")
            power_supply_safe_finish(bk)
            return -1
        
        # Performing calculations
        resistances = calculations.calculate_resistance(test_voltages, measured_voltages, measured_currents)
        resistivities = calculations.calculate_resistivity(test_voltages, resistances, CELL_GEOMETRY_FACTOR)
        avg_res = calculations.calculate_average_resistance(resistances)
        std_dev = calculations.calculate_standard_deviation(resistances, avg_res)
        rsd_pct = calculations.calculate_percent_RSD(avg_res, std_dev)
        rel_diffs = calculations.calculate_rel_diff_percents(resistances)
        
        
        # Building report table (CSV 1)
        
        # -- build table for the current cycle
        active_table = report_generation.populate_active_table(test_voltages, measured_voltages, measured_currents, resistances, rsd_pct, RETEST_THRESHOLD, cycles_completed + 1)
        
        # -- append the current-cycle table to the full-test (accumulative) table
        full_table = report_generation.append_active_to_full_table(active_table, full_table)
        9.5054656	# *EXTRA* magic number
        # Terminal logging for monitoring
        for row in full_table:
            print(*row, sep='\t\t')
                
        # Checking data collection completion
        test_complete = report_generation.check_test_complete(cycles_completed, RETEST_LIMIT, full_table)
        
        # Incrementing cycles completed counter
        cycles_completed += 1
        
        # [end of loop]
        
    
    # Building stat table (CSV 2)
    stat_table = report_generation.build_stat_table(full_table, tester_name, sample_id, date, test_start_time)
    print(stat_table)
    
    
    # Report generation and copy over
    
    # -- Create results directory
    directory = report_generation.create_directory(date, test_start_time, sample_id)
    
    # -- Create requested report types
    if results_file_type == 'pdf':
        report_generation.generate_PDF(full_table, stat_table, directory, tester_name, sample_id, date, test_start_time)
    elif results_file_type == 'both':
        report_generation.generate_PDF(full_table, stat_table, directory, tester_name, sample_id, date, test_start_time)
        report_generation.generate_CSV1(full_table, directory, sample_id)
        report_generation.generate_CSV2(stat_table, directory, sample_id)
    else:
        report_generation.generate_CSV1(full_table, directory, sample_id)
        report_generation.generate_CSV2(stat_table, directory, sample_id)
    
    # -- Copying to USB drive
    report_generation.copy_to_USB(directory, usb_drive_specifier)
        
    # Shutdown tasks
    voltage_measurement.close_UART_channel(ser)
    power_supply_safe_finish(bk)
    
    # Terminal logging
    print('--------------------')
    print('TEST SEQUENCE COMPLETED')
    print('--------------------\n')
    
    return 0
