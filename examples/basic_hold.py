"""Basic python program to execute a HOLD command and wait
the specified amount of time.
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

# Define TSP and wait time
TSP = 50        # In °C
TIME = 10       # In seconds

# Execute a HOLD command
print(f'Executing HOLD at {TSP}°C')
controller.hold(TSP)

# Wait for the desired amount of time in seconds
print(f'Wait for {TIME} seconds')
time.sleep(TIME)

# Check if TSP value is still the same
print(f'TSP value the same? {TSP == controller.get_set_point_temperature()}')

# Output the current PV
print(f'Current PV temperature: {controller.get_process_variable()}')

# Stop the HOLD command
print('Stopping HOLD command')
controller.stop()

# Disconnect the controller
print('Disconnecting the controller')
controller.disconnect()
