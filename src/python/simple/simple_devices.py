import pyvisa
import time
import subprocess
import serial
import math

# ================================================================
# DEVICE MANAGER
# ================================================================

class module_devices:

    def __init__(self, simulator: bool):
        
        self.adc: module_adc = module_adc(self, simulator)
        self.ps: module_ps = module_ps(self, simulator)

    def reset(self):

        self.adc.close_UART_channel()
        self.ps.set_voltage(0)
        self.ps.channel_off()

    def shutdown(self):
        
        
        
        pass

# ================================================================
# ANALOG TO DIGITAL CONVERTER
# ================================================================

PS_MANAGER = '@py'
PS_SOCKET = 'TCPIP::192.168.1.10::5025::SOCKET'
PS_PINGLAN_PATH = '../scripts/ping.sh'

class module_ps:

    def __init__(self, device: module_devices, simulator: bool):

        self.device: module_devices = device
        self.simulator: bool = simulator
        self.resource: pyvisa.Resource = None

        self.channel_enabled: bool = False
        self.target_voltage: float = 0.0
        self.hz: float = 0.0

        if (self.simulator == True):
            return

        # Try to init module
        try:   
            self.resource = pyvisa.ResourceManager(PS_MANAGER).open_resource(PS_SOCKET)
        except Exception as e:
            print("Could not initialize power supply module")
            raise
        pass

    # ================================================================
    # DEVICE CONFIG AND TESTING
    # ================================================================

    def can_ping(self) -> bool:

        # No need to ping if simulator!
        if (self.simulator == True):
            return True

        # Do what was originally done thru the ping bash script here.
        # This just checks if it's possible to ping the module.
        cmd_conf: list = ['sudo', 'nmcli', 'con', 'up', 'Wired connection 1']
        cmd_ping: list = ['ping', '-c', '3' '192.168.1.10']

        try:
            subprocess.call(cmd_conf)
            return subprocess.call(cmd_ping)
        except Exception as e:
            print(f'Error pinging lan: {e}')
            return False

    def configure_ethernet(self):

        # No need to configure if simulator!
        if (self.simulator == True):
            return
        
        # Configuration
        self.resource.timeout = 10000
        self.resource.write_termination = '\n'
        self.resource.read_termination = '\n'
        print('IDN ', self.resource.query('*IDN?').strip())
        self.resource.write('SYST:REM')
        time.sleep(2)
        
        # Terminal logging
        print('Configured ethernet')

    def startup(self):

        # Set to 60hz
        self.hz = 60.0

        # No need to configure if simulator!
        if (self.simulator == True):
            return
 
        # Setting frequency
        self.resource.write('SOUR:FREQ 60')
        
        # Check dimmer setting
        self.resource.write('SOUR:DIMM:STAT OFF') # THIS LINE needs to be checked still
        
        # Terminal logging
        print('Power supply startup settings set')

    def channel_on(self):

        self.channel_enabled = True

        # No need to configure if simulator!
        if (self.simulator == True):
            return

        self.resource.write('OUTP ON')
        print('Power supply channel ON')

    def channel_off(self):

        self.channel_enabled = False

        # No need to configure if simulator!
        if (self.simulator == True):
            return

        self.resource.write('OUTP OFF')
        print('Power supply channel OFF\n')

    # ================================================================
    # ELECTRICAL
    # ================================================================

    def set_voltage(self, voltage: float):

        self.target_voltage = voltage

        # No need to configure if simulator!
        if (self.simulator == True):
            return
        
        # Setting up the instruction string to be sent from the RaspberryPi to the power supply
        instruction = 'SOUR:VOLT ' + str(voltage)
        
        # Sending the instruction string over ethernet
        self.resource.write(instruction)
        
        # Terminal logging
        print('Voltage set to ', voltage, 'V')

    def measure_current(self) -> float:

        # No need to do a real measurement if simulator!
        if (self.simulator == True):
            return self.target_voltage / 10.0
        
        current = self.resource.query('MEAS:CURR?') * 1000
        print('Measured current ', current, ' mA')
        return current

# ================================================================
# ANALOG TO DIGITAL CONVERTER
# ================================================================

class module_adc:

    def __init__(self, device: module_devices, simulator: bool):

        self.device: module_devices = device
        self.serial: serial = None
        self.simulator: bool = simulator

        # If simulator, don't try to connect...
        if (self.simulator == True):
            return

        # Try to init module
        try:   
            self.serial = serial.Serial('/dev/ttyAMA0', 9600, timeout=2)
        except Exception as e:
            print("Could not initialize analog-to-digital converter module")
            raise
        pass

    # ================================================================
    # DEVICE CONFIG AND ELECTRICAL
    # ================================================================

    def trigger_arduino(self):

        # If simulator, don't try to connect...
        if (self.simulator == True):
            return

        # Terminal logging
        print('Requesting value from Arduino')
        
        # Formatting instruction
        instruction = 'A'.encode('utf-8')
        
        # Writing instruction to the UART channel
        self.serial.write(instruction)
        
        # Time delay
        time.sleep(1)

    def read_from_UART(self) -> float:

        # If simulator, don't try to get value
        # Instead, get a fake RMS value
        if (self.simulator == True):
            return self.device.ps.target_voltage / math.sqrt(2.0)
        
        # Terminal logging
        print('Reading from UART')
        
        # Read line, decode, and remove whitespace
        value = self.serial.readline().decode('utf-8').strip()
        print(f'value read: {value}')
        
        # Returning data if valid
        try:
            return float(value)
        except ValueError:
            print(f'Issue reading from UART: Invalid data received: {value}')
            print('Completed with warning\n')
            return 0.0

    def close_UART_channel(self):

        # If simulator, don't try to close...
        if (self.simulator == True):
            return 

        # Closing channel
        self.serial.close()
        
        # Terminal logging
        print('Closed UART channel')