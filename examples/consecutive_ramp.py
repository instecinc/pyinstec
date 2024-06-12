"""Simple python program to complete consecutive ramps with varying ramp rates.
"""

import instec
import time

tsp = [50.0, 60.0, 80.0, 90.0]      # In °C
rt = [30.0, 50.0, 100.0, 20.0]      # In °C/minute

# Initialize controller
controller = instec.instec(instec.mode.ETHERNET)
controller.connect()

for rate in rt:
    # Get current PV; we use controller.get_operating_slave() - 1 because
    # slaves are 1 indexed, meaning they start from 1, not 0
    pv = controller.get_process_variables()[
        controller.get_operating_slave() - 1]
    # Hold at TSP value for specified rate
    controller.ramp(tsp[0], rate)

    # Get start time
    start_time = time.time()

    # Wait until ramp is done by comparing TSP to current temp and
    # calculating estimated time, then execute next ramp
    time.sleep(
        max(abs((tsp[0] - pv) / rate * 60) - (time.time() - start_time), 0))

    # Remove old TSP value
    tsp.pop(0)

controller.stop()

controller.disconnect()
