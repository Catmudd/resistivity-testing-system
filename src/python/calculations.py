
MILLIAMP_CONVERSION = 1000   # Used for Ohm's Law: R(Ohms) = 1000 * V(Volts) / I(Milliamps)




def calculate_resistance(test_voltages: list[int], measured_voltages: dict[int:list[float]], measured_currents: dict[int:list[float]]) -> dict[int:list[float]]:
    """
    Calculates the resistances at each test voltage level for the measured voltage and current. If the number of measurements\
        is uneven, it is bound by whichever measurement is less populous for each test voltage level.\n
        `voltage = current / resistance`

    :param `test_voltages`: A list of integer voltage levels for which tests were run.
    :type `test_voltages`: **list [ int ]**
    :param `measured_voltages`: A dictionary with keys matching the test_voltage integer elements and with each value being a\
        list of measured voltages ordered chronologically by the time the measurement was taken.
    :type `measured_voltages`: **dict [ int \: list [ float ] ]**
    :param `measured_currents`: A dictionary with keys matching the test_voltage integer elements and with each value being a\
            list of measured currents ordered chronologically by the time the measurement was taken.
    :type `measured_currents`: **dict [ int \: list [ float ] ]**
    :rtype: `resistance` \: *dict [ int \: list [ float ] ]*
    :return: A dictionary with keys matching the test_voltage integer elements and with each value being a list of calculated\
        resistances ordered chronologically by the time the measurements were taken.
    """

    resistance = dict()
    # Looping to perform the calculation for each set of measurements
    for test_voltage in test_voltages:

        # Shouldn't even crash, but checking for potential fatal errors and reporting if needed.
        if (test_voltage not in measured_voltages) or (test_voltage not in measured_currents):
            print(f"calculate_resistance: ERROR: Missing voltage/current data for {test_voltage}V. Skipping...")
            continue
        if (len(measured_voltages[test_voltage]) == 0) or (len(measured_currents[test_voltage]) == 0):
            print(f"calculate_resistance: ERROR: Missing voltage/current data for {test_voltage}V. Skipping...")
            continue

        resistance[test_voltage] = []

        for volts, mA in zip(measured_voltages[test_voltage], measured_currents[test_voltage]):        
            # Calculating resistance for the dataset
            ohms = MILLIAMP_CONVERSION * volts / mA if mA != 0.0 else 0.0
            
            # Appending the result to the resistance array
            resistance[test_voltage].append(ohms)
    
    # Terminal logging
    print('Calculated resistance values')

    # Returning list.
    return(resistance)




def calculate_resistivity(test_voltages: list[int], resistance: dict[int:list[float]], geometry_factor: float) -> dict[int:list[float]]:
    """
    Calculates the resistivities at each test voltage level for the calculated resistance given a geometry factor.\n
        `resistivity = resistance * geometry_factor`

    :param `test_voltages`: A list of integer voltage levels for which tests were run.
    :type `test_voltages`: **list [ int ]**
    :param `resistance`: A dictionary with keys matching the test_voltage integer elements and with each value being a\
        list of calculated resistances ordered chronologically by the time the measurements were taken.
    :type `resistance`: **dict [ int \: list [ float ] ]**
    :param `geometry_factor`: A value used to multiply resistance by to account for cell length and cross-section area.
    :type `geometry_factor`: **float**
    :rtype: `resistivity` \: *dict [ int \: list [ float ] ]*
    :return: A dictionary with keys matching the test_voltage integer elements and with each value being a list of calculated\
        resistivities ordered chronologically by the time the measurements were taken.
    """
    
    resistivity = dict()
    # Looping to perform the calculation for each set of measurements
    for test_voltage in test_voltages:

        # Shouldn't even crash, but checking for potential fatal errors and reporting if needed.
        if test_voltage not in resistance:
            print(f"calculate_resistivity: ERROR: Missing resistance data for {test_voltage}V. Skipping...")
            continue
        if len(resistance[test_voltage]) == 0:
            print(f"calculate_resistivity: ERROR: Missing resistance data for {test_voltage}V. Skipping...")
            continue

        resistivity[test_voltage] = []

        for r in resistance[test_voltage]:
            # Calculating resistivity of the dataset
            rho = round(r * geometry_factor, 3)
            
            # Appending the resistivity result to the array
            resistivity[test_voltage].append(rho)
        
    # Terminal logging
    print('Calculated resistivity values')

    # Returning dictionary.
    return(resistivity)




def summarize_resistivity(resistance: dict[int:list[float]], geometry_factor: float) -> float:
    """
    Calculates and returns a summarized resistivity value, equal to the mean calculated resistance multiplied by the geometry factor.\n
        `geometry_factor * sum(resistances) / #resistance_measures`

    :param `resistance`: A dictionary with keys matching the integer test voltage levels and with each value being a\
        list of calculated resistances ordered chronologically by the time the measurements were taken.
    :type `resistance`: **dict [ int \: list [ float ] ]**
    :param `geometry_factor`: A value used to multiply resistance by to account for cell length and cross-section area.
    :type `geometry_factor`: **float**
    :rtype: `summarized_rho` \: *float*
    :return: A summarized resistivity value, equal to the mean calculated resistance multiplied by the geometry factor.
    """

    if not resistance:
        print("summarize_resistivity: ERROR: No resistance data. Aborting and returning 0.0...")
        return 0.0

    acc = 0.0
    count = 0
    for r_values in resistance.values():
        acc += sum(r_values)
        count += len(r_values)
    
    avg_resistance = acc / count if count != 0 else 0.0
    summarized_rho = avg_resistance * geometry_factor
    
    print('Calculated dataset summarized resistivity')
    
    return summarized_rho




def calculate_average_resistance(resistance: dict[int:list[float]]) -> float:
    """
    Calculates and returns the mean resistance from the calculated resistance values.\n
        `sum(resistances) / #resistance_measures`

    :param `resistance`: A dictionary with keys matching the integer test voltage levels and with each value being a\
        list of calculated resistances ordered chronologically by the time the measurements were taken.
    :type `resistance`: **dict [ int \: list [ float ] ]**
    :rtype: `avg_res` \: *float*
    :return: The mean of the calculated resistance values.
    """
    
    acc = 0.0
    count = 0

    for r_values in resistance.values():
        acc += sum(r_values)
        count += len(r_values)

    avg_res = round(acc / count, 3) if count != 0 else 0.0
    print('Calculated average resistance')
    return avg_res




def calculate_standard_deviation(resistance: dict[int:list[float]], avg_res: float) -> float:
    """
    Calculates and returns the standard deviation of the measured resistance values.\n
        `standard_deviation = sqrt( sum((resistance - average)^2 / #resistance_measures)) [for all resistance measures]`

    :param `resistance`: A dictionary with keys matching the integer test voltage levels and with each value being a\
        list of calculated resistances ordered chronologically by the time the measurements were taken.
    :type `resistance`: **dict [ int \: list [ float ] ]**
    :param `avg_res`: The mean of the calculated resistance values.
    :type `avg_res`: **float**
    :rtype: `std_dev` \: *float*
    :return: The standard deviation of the measured resistance values.
    """

    acc = 0.0
    count = 0

    for r_values in resistance.values():
        acc += sum((r - avg_res) ** 2 for r in r_values)
        count += len(r_values)

    variance = acc / (count - 1) if count > 1 else 0.0
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
def calculate_percent_RSD(avg_res: float, std_dev: float) -> float:
    rsd_pct = (100.0 * std_dev / avg_res) if avg_res != 0.0 else 0.0
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
    
def calculate_rel_diff_percents(resistance: dict[int:list[float]]) -> dict[int:float]:
    # n = len(resistance)
    # if n%9 != 0:
    #     raise ValueError(f"Resistance list length must be a multiple of 9 (got {n})")
    # if n == 0:
    #     pair_diffs.extend([0.00]*4)
    #     return
    if not resistance:
        print("calculate_rel_diff_percents: ERROR: No resistance data. Aborting difference calculations...")
        return dict()

    rel_diffs = dict()

    for test_voltage in resistance.keys():
        if len(resistance[test_voltage]) == 0:
            print(f"calculate_rel_diff_percents: ERROR: Missing resistance data for {test_voltage}V. Skipping...")
            continue

        rel_diffs[test_voltage] = []
    
    # num_trials = n // 9
    # pair_indices = [(0, 8), (1, 7), (2, 6), (3, 5)]
    
    # for a, b in pair_indices:
        
    #     #identify and collect 2/4/6 values to perform calculation
    #     pair_values = []
    #     for trial in range(num_trials):
    #         offset = trial*9
    #         pair_values.append(resistance[offset+a])
    #         pair_values.append(resistance[offset+b])
    #     if len(pair_values) < 2:
    #         pair_diffs.append(0.00)
    #         continue
        
        #calculate the percent difference between the min and max values of this list
        vmin = min(resistance[test_voltage])
        vmax = max(resistance[test_voltage])
        # vmin = min(pair_values)
        # vmax = max(pair_values)
        rel_diff_pct = 100 * (vmax - vmin) / vmin if vmin != 0.0 else 0.0
        
        # pair_diffs.append(round(rel_diff_pct, 2))
        rel_diffs[test_voltage].append(round(rel_diff_pct, 2))

    return rel_diffs

