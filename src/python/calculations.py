
MILLIAMP_CONVERSION = 1000   # Used for Ohm's Law: R(Ohms) = 1000 * V(Volts) / I(Milliamps)

#----------------------------------------
# calculate_resistance(measured_voltages, measured_currents, resistance)
#
# parameters:
#	- measured_voltages   : array containing the measured voltage value for each applied voltage
#	- measured_currents   : array containing the measured current value for each applied voltage
#
# function description:
#	Calculates 9 resistances (one for each set of voltages/currents in the data arrays) using Ohm's Law. 
#----------------------------------------

def calculate_resistance(measured_voltages: list[float], measured_currents: list[float]) -> list[float]:
    resistance = []
    # Looping to perform the calculation for each set of measurements
    # NEW LOOP REQUIRES FAILED TESTS TO DROP BOTH VOLTAGE AND CURRENT FOR THAT TEST.
    for volts, mA in zip(measured_voltages, measured_currents):
        # Calculating resistance for the dataset
        ohms = MILLIAMP_CONVERSION * volts / mA
        
        # Appending the result to the resistance array
        resistance.append(ohms)
    
    # Terminal logging
    print('Calculated resistance values')

    # Returning list.
    return(resistance)



#----------------------------------------
# calculate_resistivity(resistance, resistivity, geometry_factor)
# Potentially redundant function because BPA only calculate 1 resistivity value from the 1 average resistance. They do not calculate 9 resistivity values for all 9 trials. 
# 
# parameters:
#	- resistance: array containing the calculated resistance for each applied voltage.
#	- geometry_factor: multiply this with the resistance to get resistivity (accounts for cell length and cross-section area)
#
# function description:
#	- Calculates 9 resistivity values (one for each set of voltages/currents)
#----------------------------------------

def calculate_resistivity(resistance: list[float], geometry_factor: float) -> list[float]:
    resistivity = []
    # Looping to perform the calculation for each set of measurements
    for r in resistance:
        # Calculating resistivity of the dataset
        rho = round(r * geometry_factor, 3)
        
        # Appending the resistivity result to the array
        resistivity.append(rho)
        
    # Terminal logging
    print('Calculated resistivity values')

    # Returning list.
    return(resistance)



#----------------------------------------
# summarize_resistivity(resistance, geometry_factor)
# 
# Parameters:
#    resistance       : List of calculated resistance values (ohms) from all voltage steps
#    geometry_factor  : Cell constant (cm) that accounts for length and cross-sectional area
#    
# Returns:
#    float: Summarized resistivity value (average resistance × geometry factor)
#           Returns 0.0 if the resistance list is empty
#    
# Example:
#    resistance = [1000, 1010, 990, 1005]
#    geometry_factor = 0.33
#    → returns ≈ 330.0
#----------------------------------------

def summarize_resistivity(resistance, geometry_factor) -> float:
    if not resistance:
        print("Warning: No resistance values provided → returning 0.0")
        return 0.0
    
    avg_resistance = sum(resistance) / len(resistance)
    summarized_rho = avg_resistance * geometry_factor
    
    print('Calculated dataset summarized resistivity')
    
    return summarized_rho



#----------------------------------------
# calculate_average_resistance(resistance, avg_res)
#
# parameters:
#	- resistance: array containing the calculated resistance for each applied voltage
#	- avg_res: variable to hold the calculated result
#----------------------------------------

def calculate_average_resistance(resistance, avg_res):
    avg_res = float(round(sum(resistance) / len(resistance), 3))
    print('Calculated average resistance')
    return avg_res



#----------------------------------------
# calculate_standard_deviation(resistance, avg_res, std_dev)
#
# parameters:
#	- resistance: array containing the calculated resistance for each applied voltage.
#	- avg_res: the calculated average of the resistances. 
#	- std_dev: value to hold the calculated standard deviation. 
#----------------------------------------

def calculate_standard_deviation(resistance, avg_res, std_dev):
    #avg_res = float(avg_res)
    variance = sum((x - avg_res) ** 2 for x in resistance) / (len(resistance) - 1)
    std_dev = variance ** 0.5
    print('Calculated standard deviation')
    return std_dev



#----------------------------------------
# calculate_percent_RSD(avg_res, std_dev, rsd_pct)
#
# parameters:
#	- avg_res: the calculated average of the resistances. 
#	- std_dev: the calculated standard deviation value.
#	- rsd_pct: value to hold the calculated % RSD value. 
#
# function description:
#	Matches the BPA Excel % RSD calculation.
#	% RSD = (standard_deviation / mean) * 100
#----------------------------------------
def calculate_percent_RSD(avg_res, std_dev, rsd_pct):
    rsd_pct = (100.0 * std_dev / avg_res) if avg_res !=0 else 0.0
    return rsd_pct
    
    
    
#----------------------------------------
# calculate_rel_diff_percents(resistance, pair_diffs)
#
# parameters:
#	- resistance: array containing the calculated resistance for each applied voltage.
#	- pair_diffs: empty array to  be filled with the 4 relative difference % values. 
#
# function description:
#	Calculates the percent differences between min/max for symmetric "Pairs" (or 2/4/6 values for 9/18/27 data points)
#	The result is an array with 4 values (the values are stored in the passed-in array 'pair_diffs' as shown:
#		[1&9 Diff, 2&8 Diff, 3&7 Diff, 4&6 Diff]
#----------------------------------------
    
def calculate_rel_diff_percents(resistance, pair_diffs):
    n = len(resistance)
    if n%9 != 0:
        raise ValueError(f"Resistance list length must be a multiple of 9 (got {n})")
    if n == 0:
        pair_diffs.extend([0.00]*4)
        return
    
    num_trials = n // 9
    pair_indices = [(0, 8), (1, 7), (2, 6), (3, 5)]
    
    for a, b in pair_indices:
        
        #identify and collect 2/4/6 values to perform calculation
        pair_values = []
        for trial in range(num_trials):
            offset = trial*9
            pair_values.append(resistance[offset+a])
            pair_values.append(resistance[offset+b])
        if len(pair_values) < 2:
            pair_diffs.append(0.00)
            continue
        
        #calculate the percent difference between the min and max values of this list
        vmin = min(pair_values)
        vmax = max(pair_values)
        if vmin==0:
            rel_diff_pct = 0.0 #avoid dividing by 0
        else:
            rel_diff_pct = 100*(vmax - vmin)/vmin
        
        pair_diffs.append(round(rel_diff_pct, 2))











###
### THIS FUNCTION IS UNUSED --- comparison of %RSD and threshold is done in report_gen.populate_active_table()
###
# def evaluate_retest_criteria(rsd_pct, retest_threshold) -> bool:
#     return rsd_pct <= retest_threshold
