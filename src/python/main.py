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

test_voltages = [50, 100, 150, 200, 250] # Keeping static for now, will need to be made dynamic.

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
def take_sample(bk, ser, test_voltage, measured_currents: dict[int:list[float]], measured_voltages: dict[int:list[float]]) -> bool:

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

    measured_voltages[test_voltage].append(read_voltages[0])
    return volt_pass

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
        # Don't necessarily need to be instantiated, but preserving current flow.
        # measured_currents = []
        # measured_voltages = []
        # resistance = []     # Updated - can be removed.
        resistivity = []    # Updated - can be removed.
        
        pair_diffs = []
        
        # Clearing stat values for next cycle
        avg_resistivity = 0.0
        avg_res = 0.0
        std_dev = 0.0
        rsd_pct = 0.0
    
        
        # Looping through the set of applied voltages.
        # Try taking a sample, but if something excepts,
        # safely shut off hardware and re-emit the error.
        for test_voltage in test_voltages:

            measured_voltages = dict()
            measured_voltages[test_voltage] = []
            measured_currents = dict()
            measured_currents[test_voltage] = []
            
            try: 
                if not take_sample(bk, ser, test_voltage, measured_currents, measured_voltages):
                    print(f"Voltage {test_voltage} failed. Continuing...")
            except:
                voltage_measurement.close_UART_channel(ser)
                power_supply_safe_finish(bk)
                raise
    
        
        # Performing calculations
        resistance = calculations.calculate_resistance(test_voltages, measured_voltages, measured_currents)
        resistivity = calculations.calculate_resistivity(resistance, cell_geometry_factor)
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
    power_supply_safe_finish(bk)
    
    # Terminal logging
    print('--------------------')
    print('TEST SEQUENCE COMPLETED')
    print('--------------------\n')
    
    return 0
