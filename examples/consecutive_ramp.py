"""Python program that executes several consecutive
RAMP commands, delaying the next RAMP command based on
the estimated time to finish.
"""

import instec
import time


# Variables for setting up the controller
MODE = instec.mode.USB      # Connection mode
BAUD = 38400                # Baud rate for USB mode
PORT = 'COM3'               # Port for USB mode

# Initialize controller and connect
controller = instec.MK2000(MODE, BAUD, PORT)
controller.connect()

# Define the set of TSP and RT values to use
tsp = [50.0, 60.0, 80.0, 90.0]      # In °C
rt = [30.0, 50.0, 80.0, 20.0]      # In °C/minute

# For each RT value:
for rate in rt:
    # Get current PV
    pv = controller.get_process_variable()
    # RAMP to TSP value at specified RT
    controller.ramp(tsp[0], rate)

    # Wait until RAMP is done by calculating the estimated time
    # based on RT and the temperature delta, then execute next RAMP
    time.sleep(abs((tsp[0] - pv) / rate * 60))

    # Remove old TSP value
    tsp.pop(0)

# Stop the RAMP command
print('Stopping RAMP command')
controller.stop()

# Disconnect the controller
print('Disconnecting the controller')
controller.disconnect()
