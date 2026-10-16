#----------------------------------------
# Library Imports
#----------------------------------------

import time
import serial
import os
import shutil
import subprocess
import csv
import calculations
from datetime import datetime
from fpdf import FPDF

import troubleshoot
    


#----------------------------------------
# check_for_connected_USB()
#
# function description:
#	This function is run at startup and checks if a USB drive has been
#	connected to one of the USB-A ports on the Raspberry Pi (to receive the result
#	files at the end of testing). If one is detected, its identifier is returned so
#	it can be used later by the file copy over functionality. If a drive is not
#	detected, a troubleshoot function is run to notify the user and allow them to
#	connect a USB drive before continuing. 
#----------------------------------------

def check_for_connected_USB(): 
    try:
        output = subprocess.check_output('df -h | grep /media', shell=True, text=True, stderr=subprocess.STDOUT)
        
        if output.strip():
            print('USB drive detected: ', output)
            
            # Getting starting index of the drive identifier
            index = output.find('/media/wsucapstone/')
            
            # Formatting a string to contain the identifier / drive destination
            usb_destination = output[index:].rstrip()
            
            # Terminal logging --- showing the USB drive identifier
            print(usb_destination)
            
            # Returning the usb_destination (in the case that a USB drive was detected)
            return usb_destination
        else:
            print('No USB drive was detected\n')
    
    except subprocess.CalledProcessError as e:
        print('No USB drive was detected\n')
    
    
    # If program flow reaches this point --> no USB drive was detected; so, call troubleshoot function
    troubleshoot.USB_not_detected()
    
    # Try detecting one more time
    try:
        output = subprocess.check_output('df -h | grep /media', shell=True, text=True, stderr=subprocess.STDOUT)
            
        if output.strip():
            print('USB drive detected: ', output)
            index = output.find('/media/wsucapstone/')
            usb_destination = output[index:].rstrip()
            print(usb_destination)
            return usb_destination
        else:
            print('No USB drive was detected\n')
            return 0
        
    except subprocess.CalledProcessError as e:
        print('No USB drive was detected\n')
        return 0


#----------------------------------------
# copy_to_USB()
#
# parameters:
#	- source_path		: directory path to the file 
#	- destination_path	: directory path to the destination (which is the USB drive)
#
# function description:
#	Copies the folder specified by the source path (which is the directory containing all
#	result files for the resistivity test) to the destination path (which is the USB drive
#	that is connected to the Raspberry Pi). 
#----------------------------------------

def copy_to_USB(source_path, destination_path):
    # Copying
    try:
        #shutil.copy(source_path, destination_path)
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
        print('folder copy over was successful')
    except FileNotFoundError:
        print('file not found')
    except PermissionError:
        print('permission error')
    except Exception as e:
        print('other error type in USB copy over')
        print(e)
    
    # Terminal logging
    print('Copied results to USB drive')



#----------------------------------------
# create_directory(date, time, sample_id)
#
# parameters:
#	- date       : test date
#	- time       : test start time
#	- sample_id  : test sample ID
#
# function description: 
# 	Creates a new directory in the 'Reports' folder to hold
# 	the result files for the test.

# 	Note: a directory is made for each test that is run because
# 		multiple result files are generated per test (csv1 and csv2, and also
# 		pdf if user selects csd & pdf), and also because the report file names
# 		don't specify the test date, time, sample id (for the default CSV report type). 
#----------------------------------------

def create_directory(date, time, sample_id):
    # New folder to hold all result files for the resistivity test
    new_folder = str(date) + ' ' + str(time) + ' SID' + str(sample_id)
    
    # All result folders are located in the 'Reports' folder
    parent_folder = '/home/wsucapstone/capstone/Reports'
    #parent_folder = 'Reports'
    
    # Path to the new directory
    new_folder_path = os.path.join(parent_folder, new_folder)
    
    # Try to create the directory
    try:
        os.makedirs(new_folder_path, exist_ok=True)
        print('Results directory created')
    except OSError as e:
        print('Error creating directory')

    # Return the directory so the main.py logic can access the directory path and know where to put generated result files
    return new_folder_path



#----------------------------------------
# generate_CSV1(table, directory)
#
# parameters:
#	- table      : the data table to be converted to a CSV file. 
#	- directory  : the result directory to place the CSV file.
#	- sample_id  : sample ID, to give the file a unique name. 
#
# function description:
# 	Creates the the csv_1 file in the specified directory. 
#
#----------------------------------------

def generate_CSV1(table, directory, sample_id):
    
    # Path to the csv file
    file_name = 'csv_1 ID' + sample_id + '.csv'
    path = os.path.join(directory, file_name)
    
    # Creating / opening the csv file and writing the data to the file
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(table)
    
    print('Generated csv_1')
    
    
    
#----------------------------------------
# generate_CSV2(table, directory)
#
# parameters:
#	- table      : the statistics table to be converted to a CSV file. 
#	- directory  : the result directory to place the CSV file.
#	- sample_id  : sample ID, to give the file a unique name. 
#
# function description:
#	Creates the csv_2 file in the specified directory. 
#
#----------------------------------------

def generate_CSV2(table, directory, sample_id):
    
    # Path to the CSV file
    file_name = 'csv_2 ID' + sample_id + '.csv'

    path = os.path.join(directory, file_name)
    
    # Creating / opening the csv file and writing the date to the file
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(table)
    
    print('Generated csv_2')

    

#----------------------------------------
# populate_active_table(test_voltages, measured_voltages, measured_currents, resistance, rsd_pct, retest_threshold, cycles_completed)
#
# parameters:
#	- test_voltages       : list of applied voltages (in Volts) : [50, 100, 150, 200, 250, 200, 150, 100, 50]
#	- measured_voltages   : list of measured voltages, one for each applied voltage (in corresponding list indices)
#	- measured_currents   : list of measured currents, one for each applied voltage (in corresponding list indices)
#	- resistance          : list of calculated resistances, one for each applied voltage (in corresponding list indices)
#	- rsd_pct             : relative standard deviation percent, a single value calculated for the dataset
#	- retest_threshold    : A value (percentage) that rsd_pct cannot exceed without requiring a retest
#	- cycles_completed    : Loop counter variable, keeping track of the number of test loop cycles completed in main.py
#
# returns:
#	- ACTIVE_TABLE : The populated table created. 
#
# function description:
#	Builds the data table for the current test cycle (contains 9 rows, one for each applied voltage in the test cycle).
#	Each row contains a value for the following sections: 
# 		["V Applied", "V Measured", "Current", "Resistance", "Trial_ID", "Pass_ID"]
#----------------------------------------
    
def populate_active_table(test_voltages, measured_voltages, measured_currents, resistance, rsd_pct, retest_threshold, cycles_completed):
    # Empty array to be filled with the active table
    ACTIVE_TABLE = []
    
    # Building each row of the table and appending it to the table
    for i in range(len(test_voltages)):
        # Building the 'i' row of the active table
        row = []
        row.append(test_voltages[i])
        row.append(measured_voltages[i])
        row.append(measured_currents[i])
        row.append(resistance[i])
        row.append(cycles_completed)
        row.append('pass' if rsd_pct <= retest_threshold else 'fail')
        
        # Appending the 'i' row to 'ACTIVE_TABLE'
        ACTIVE_TABLE.append(row)
    
    print('Populated active table')
    
    return ACTIVE_TABLE
    
    

#----------------------------------------
# append_active_to_full_table(ACTIVE_TABLE, FULL_TABLE)
#
# parameters:
#	- ACTIVE_TABLE: The data table for the current cycle of the test loop
#	- FULL_TABLE: The cumulative data table across all cycles of the test loop (to be appended to)
#
# returns:
#	- FULL_TABLE: The cumulative table with the active table appended to it 
#
# function description:
#	Appends the current-cycle data table to the cumulative table and returns the combined table 
#----------------------------------------
def append_active_to_full_table(ACTIVE_TABLE, FULL_TABLE):
    FULL_TABLE = FULL_TABLE + ACTIVE_TABLE
    print('Appended active to full table')
    return FULL_TABLE

    

#----------------------------------------
# check_test_complete(cycles_completed, retest_limit, FULL_TABLE)
#
# parameters:
#	- cycles_completed   : loop cycle counter from the test loop in main.py
#	- retest_limit       : Hard-coded test parameter value indicating the maximum number of re-tests
#	- FULL_TABLE         : The data table containing a row for data from each applied voltage

# function description:
#	Checks if the test loop should stop or continue --> STOP if >= 27 'pass' rows of data have been collected, or retest limit reached; otherwise CONTINUE
#----------------------------------------
def check_test_complete(cycles_completed, retest_limit, FULL_TABLE): 
    
    test_complete = False # initial value of test_complete (not complete until the evaluation finds the test is complete)
    success_count = 0
    
    # Counting the numer of passes
    for row in FULL_TABLE:
        if row[5] == 'pass':
            success_count = success_count + 1
    
    # Evaluating pass/fail (if success count >= 27 or retest limit exceeded ---> stop testing)
    if cycles_completed > retest_limit or success_count >= 27:
        print('Criteria met to end test data collection')
        test_complete = True
    
    # Returning test_complete (True or False)
    return test_complete

#----------------------------------------
# build_stat_table(table)
#
# parameters:
#	- table             : Data table containing a row for the measured data from each applied voltage case (at least 27 rows)
#	- tester_name       : Name of tester (entered in the user interface menu)
#	- sample_id         : Sample ID (entered in the user interface menu)
#	- date              : Date of test (collected by the code at interface startup)
#	- test_start_time   : Time of test start (collected by the code at interface startup)
#
# function description:
#	Uses the data table containing at least 27 rows (to satisfy the 27 'pass' case
#	requirement) and the test parameters to create the statistics summary table for
#	the full test. 
#----------------------------------------

def build_stat_table(table, tester_name, sample_id, date, test_start_time):
    # Step 1: Extract exactly 27 pass resistances
    passed_res27 = []
    for row in table[1:]:           # skip header
        if row[5] == "pass":
            passed_res27.append(row[3])
    
    if len(passed_res27) < 27:
        print(f"Warning: Only {len(passed_res27)} pass rows collected (expected 27)")
        # Can still proceed with what we have, or return zeros, etc.
    

    # Step 2: Warning checks
    num_passes = len(passed_res27)

    if num_passes < 27:
        print(f"Warning: Only {num_passes} pass rows found (expected exactly 27). "
              f"Using available values for statistics.")
    
    elif num_passes > 27:
        print(f"Warning: Too many passes detected ({num_passes} found, expected exactly 27). "
              f"Using only the first 27 pass values for statistics.")
        passed_res27 = passed_res27[:27]  # enforce exactly 27

    # If still empty (extremely unlikely), return safe defaults
    if num_passes == 0:
        print("Error: No pass rows found → returning zero statistics")
        return ["No successful data to report."]
    
    # Step 3: Prepare variables 
    resistance = passed_res27[:]    # copy so we don't modify original if needed
    avg_res = 0.0
    std_dev = 0.0
    rsd_pct = 0.0
    pair_diffs = []

    
    # Step 4: Reuse the calculation functions
    avg_res = calculations.calculate_average_resistance(resistance, avg_res)
    std_dev = calculations.calculate_standard_deviation(resistance, avg_res, std_dev)
    rsd_pct = calculations.calculate_percent_RSD(avg_res, std_dev, rsd_pct)
    calculations.calculate_rel_diff_percents(resistance, pair_diffs)

    
    # Step 5: Calculate average resistivity (simple multiplication)
    geometry_factor = 0.33
    avg_rho = round(avg_res * geometry_factor, 3)  # match your rounding style
    
    # Step 6: Build the output table
    STAT_TABLE = [
        ["Average Resistance", round(avg_res, 3)],   # ensure consistent rounding
        ["Average Resistivity", avg_rho],
        ["Standard Deviation", round(std_dev, 3)],
        ["RSD Percent", round(rsd_pct, 3)],
        ["1&9 Diff", pair_diffs[0]],
        ["2&8 Diff", pair_diffs[1]],
        ["3&7 Diff", pair_diffs[2]],
        ["4&6 Diff", pair_diffs[3]],
        ["Tested By", tester_name],
        ["Sample_ID", sample_id],
        ["Date", date],
        ["Time", test_start_time]
    ]
    
    return STAT_TABLE





def generate_PDF(data_table, stat_table, directory, tester_name, sample_id, date, time):
    
    # Preparing file path
    file_name = 'PDF Report' + sample_id + '.pdf'
    path = os.path.join(directory, file_name)
    
    
    # PDF setup
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    
    # Header content
    pdf.cell(w=0, h=5, txt='Rock Resistivity Test Results', ln=1, align='L')
    
    text = 'Tested by ' + tester_name
    pdf.cell(w=0, h=5, txt=text, ln=1, align='L')
    
    text = 'Sample ID: ' + str(sample_id)
    pdf.cell(w=0, h=5, txt=text, ln=1, align='L')
    
    text = 'Tested on ' + time + ' ' + date
    pdf.cell(w=0, h=5, txt=text, ln=1, align='L')
    
    
    pdf.cell(w=0, h=5, txt=' ', ln=1, align='L') # spacer
    
    
    pdf.cell(0, 0, '', 'T') # formatting line
    
    
    
    pdf.set_font('Arial', '', 8)
    
    
    
    # Data Table (CSV 1)
    pdf.cell(w=0, h=10, txt='Table 1. Measured Data & Calculated Resistance', ln=1, align='L')
    
    with pdf.table() as table:
        for data_row in data_table:
            row = table.row()
            for item in data_row:
                row.cell(str(item))
    
    pdf.cell(w=0, h=5, txt=' ', ln=1, align='L')
    
    pdf.add_page()
    
    
    # Stat Table (CSV 2)
    pdf.cell(w=0, h=10, txt='Table 2. Dataset Statistics Results', ln=1, align='L')
    
    try:
        with pdf.table(first_row_as_headings=False) as table:
            for data_row in stat_table:
                row = table.row()
                for item in data_row:
                    row.cell(str(item))
    except Exception as e:
        print('Statistics table build failed: ', e)
                
    
    # Creating file
    pdf.output(path)
    
    return 0
    
    
