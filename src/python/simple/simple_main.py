import time
import math
from simple_devices import module_devices

VOLT_WAIT_PASS_NUM: float = 4
VOLT_WAIT_SEC: float = 0.1
VOLT_WAIT_MAX_SAMPLES: float = 20
VOLT_WAIT_DEVIANCE: float = 10
VOLT_WAIT_ERROR: float = 260

SQRT2 = math.sqrt(2.0)
TEST_INDICES: list[int] = [0, 1, 2, 3, 4, 3, 2, 1, 0]
TEST_TRG_AND_EXP: list[tuple[float, float]] = [
    (50, 50 / SQRT2), 
    (100, 100 / SQRT2), 
    (150, 150 / SQRT2), 
    (200, 200 / SQRT2), 
    (250, 250 / SQRT2)]

class voltage_data:

    def __init__(self, voltage: float, current: float, passed: bool):
        self.voltage: float = voltage
        self.current: float = current
        self.passed: bool = passed

def log_data(log: dict[int, list[voltage_data]], test_id: int, data: voltage_data):
    
    if (not log.__contains__(test_id)):
        log[test_id] = [data]
    else:
        log[test_id].append(data)

def log_dump(log: dict[int, list[voltage_data]]):
    for voltage_index in range(0, TEST_TRG_AND_EXP.__len__()):
        ln = f'Target Voltage {TEST_TRG_AND_EXP[voltage_index][0]}:\n'
        for data in log[voltage_index]:
            ln += f'\n\tVoltage: {data.voltage}\n\tCurrent: {data.current}\n\tPassed: {data.passed}\n'
        print(ln)

def average(values: list[float]) -> float:
    
    sum: float = 0
    for v in values:
        sum += v
    return sum / values.__len__()

def is_v_approx_n(v, n, epsilon):
    return v > n - epsilon and v < n + epsilon

def try_wait_for_voltage_pass(devices: module_devices, voltage_expected: float, read_voltages: list[float]) -> bool:

    read_voltages.clear()

    for i in range(VOLT_WAIT_MAX_SAMPLES):

        time.sleep(VOLT_WAIT_SEC)

        # Read voltage and stick it into buffer head.
        devices.adc.trigger_arduino()
        read_voltage: float = devices.adc.read_from_UART()
        read_voltages.insert(0, read_voltage)

        # print(f'Read voltage {read_voltage}')

        # Catch unnacceptable voltages.
        if (read_voltages[0] < 0 or read_voltages[0] > VOLT_WAIT_ERROR):
            raise Exception(f'Voltage exceeded safety bounds ({read_voltages[0]}).')

        # Wait until has at least taken VOLT_WAIT_PASS_NUM samples
        # to actually check samples and see if they're all within bounds.
        if (i < VOLT_WAIT_PASS_NUM-1):
            continue

        # If most recent VOLT_WAIT_PASS_NUM samples fall within max deviance, 
        # great! We can return true. Otherwise, keep re-checking until timeout.
        if all(is_v_approx_n(voltage, voltage_expected, VOLT_WAIT_DEVIANCE) for voltage in read_voltages[0:VOLT_WAIT_PASS_NUM]):
            return True
    
    return False

def test_voltage(devices: module_devices, voltage_target: float, voltage_expected: float) -> voltage_data:

    devices.ps.set_voltage(voltage_target)
    devices.ps.channel_on()

    read_voltages: list[float] = []
    passed = try_wait_for_voltage_pass(devices, voltage_expected, read_voltages)
    average_voltage = average(read_voltages[0:VOLT_WAIT_PASS_NUM])
    read_current = devices.ps.measure_current()

    devices.ps.channel_off()

    return voltage_data(average_voltage, read_current, passed)

def test(devices: module_devices, log: dict[int, list[voltage_data]]) -> bool:


    test_number = 0
    passed = True

    for voltage_index in TEST_INDICES:

        voltage_target = TEST_TRG_AND_EXP[voltage_index][0]
        voltage_expected = TEST_TRG_AND_EXP[voltage_index][1]
        data: voltage_data = test_voltage(devices, voltage_target, voltage_expected)

        # Don't pass if a test failed
        if data.passed == False:
            passed = False

        print(f'================================================================')
        print(f'Test Number: {test_number}, Voltage Index: {voltage_index}')
        print(f'Target voltage: {voltage_target}')
        print(f'Expected voltage: {voltage_expected}')
        print(f'Actual Average Voltage: {data.voltage}')
        print(f'Passed: {data.passed}')
        print(f'================================================================')
        
        log_data(log, voltage_index, data)
        test_number += 1

    return passed

if __name__ == '__main__':

    devices = module_devices(True)

    devices.ps.can_ping()
    devices.ps.configure_ethernet()
    devices.ps.startup()

    log: dict[int, list[voltage_data]] = dict()
    print(f'All Tests passed: {test(devices, log)}')
    log_dump(log)