"""Simple python example program that prints out
various information from the controller.
"""

import instec   # Import instec library
import time

# Initialize Serial interface
controller = instec.controller(mode=instec.mode.ETHERNET)
# Attempt to connect to controller
controller.connect()
# Check connection
print(f'Connected?: {controller.is_connected()}')

delay = 1.0                               # Delay (in seconds)
start = time.time()                       # Start time

print(controller.get_pv_unit_type())
print(isinstance(instec.mode.ETHERNET, instec.mode))
print(controller.get_pid(instec.PID_table.COOLING_HNC, 5))

for i in range(1):
    # Call system ID function
    company, model, serial, firmware = controller.get_system_information()
    print(f'Company: {company}\n'
          f'Model: {model}\n'
          f'Serial number: {serial}\n'
          f'Firmware version: {firmware}\n')

    # Call rtin function - returns tuple, see library for more information
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

    # Call ramp rate range function
    print('Ramp Rate Range: '
          f'{str(controller.get_ramp_rate_range())}\n')

    # Call cooling status function
    print('Cooling/Heating Status: '
          f'{controller.get_cooling_heating_status()}\n')

    # Attempt to call the function every delay amount
    time.sleep(delay - ((time.time() - start) % delay))

controller.disconnect()

# Check connection
print(f'Connected?: {controller.is_connected()}')