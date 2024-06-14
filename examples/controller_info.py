"""Python program that prints out various system
and runtime related information about the controller.
"""

import instec
import time


# Variables for setting up the controller
MODE = instec.mode.USB      # Connection mode
BAUD = 38400                # Baud rate for USB mode
PORT = 'COM3'               # Port for USB mode

# Initialize controller and connect
print('Connecting to the controller')
controller = instec.MK2000(MODE, BAUD, PORT)
controller.connect()

# Check connection - should be True
print(f'Connected?: {controller.is_connected()}')

# Define delay (time between function calls) and number of loops
DELAY = 1.0                               # Delay (in seconds)
LOOPS = 10                                # Number of loops

# Save start time of loop
start = time.time()                       # Start time

# Adjust range to run this loop more than once
for i in range(LOOPS):
    # Call system ID function
    company, model, serial, firmware = controller.get_system_information()

    # Print system information
    print(f'Company: {company}\n'
          f'Model: {model}\n'
          f'Serial number: {serial}\n'
          f'Firmware version: {firmware}\n')

    # Call runtime information function
    data = controller.get_runtime_information()
    sx = data[0]
    pv = data[1]
    mv = data[2]
    tsp = data[3]
    csp = data[4]
    rt = data[5]
    pp = data[6]
    s_status = data[7]
    p_status = data[8]
    p = data[9]
    i = data[10]
    error_status = data[11]

    # Print runtime information
    print(f'Slave number: {sx}\n'
          f'PV: {pv}\n'
          f'MV: {mv}\n'
          f'TSP: {tsp}\n'
          f'CSP: {csp}\n'
          f'RT: {rt}\n'
          f'PP: {pp}\n'
          f'System Status: {s_status}\n'
          f'Profile Status: {p_status}\n'
          f'Active Profile Number: {p}\n'
          f'Instruction Index: {i}\n'
          f'Error Status: {error_status}\n')

    # Call ramp rate range function and print
    print('Ramp Rate Range: '
          f'{str(controller.get_ramp_rate_range())}\n')

    # Call cooling status function and print
    print('Cooling/Heating Status: '
          f'{controller.get_cooling_heating_status()}\n')

    # Attempt to delay for next function call
    time.sleep(DELAY - ((time.time() - start) % DELAY))

# Disconnect the controller
controller.disconnect()

# Check connection - should be False
print(f'Connected?: {controller.is_connected()}')
