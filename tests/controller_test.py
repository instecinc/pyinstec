"""controller_test.py defines helper functions for all other tests.

Set the correct MODE, BAUD, and PORT to connect to the specified controller.

The STEP_COUNT and UPDATE_DELAY variables should be updated accordingly
before running tests.

STEP_COUNT adjusts the number of steps certain tests take within the
defined temperature range. Alternatively, STEP_SIZE can be used to set a
constant step size. Due to Python constraints, STEP_SIZE should be an int.

UPDATE_DELAY accounts for how long the controller takes to update values
internally. If a test fails from to an assertion error due to the controller
returning a previous value, try increasing UPDATE_DELAY accordingly.

RT is a constant that is an arbitrary constant ramp rate value used for
some tests. Ensure this is within the ramp rate range of the controller
being tested.

TEST_PROFILE defines the profile that will be used for all profile tests.
This profile will be overwritten during testing, so ensure that desired
profile information is saved.
"""


import unittest
import sys
import os

# Run tests using local copy of library - comment this out if unnecessary
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import instec


class controller_test(unittest.TestCase):
    # Variables for setting up the controller
    MODE = instec.mode.USB      # Connection mode
    BAUD = 38400                # Baud rate for USB mode
    PORT = 'COM3'               # Port for USB mode

    # Constants for testing
    UPDATE_DELAY = 0.25     # in seconds, so queries don't read old values
    STEP_COUNT = 8          # Number of steps for each TSP loop
    STEP_SIZE = None        # OPTIONAL - Overrides STEP_COUNT and
                            # defines a step size instead
    RT = 5                  # Default ramp rate for some tests
    TEST_PROFILE = 4        # Profile that tests use - will be OVERWRITTEN

    def setUp(self):
        """Called at the start of each test.
        """
        self._initialize_controller()

    def tearDown(self):
        """Called at the end of each test.
        """
        self._shutdown_controller()

    def _initialize_controller(self):
        """Initialize and connect to controller using MODE, BAUD, and PORT,
        then check connection.
        """
        self._controller = instec.MK2000(self.MODE, self.BAUD, self.PORT)
        self._controller.connect()
        self.assertTrue(self._controller.is_connected())

    def _shutdown_controller(self):
        """Disconnect from controller, then check connection.
        """
        self._controller.disconnect()
        self.assertFalse(self._controller.is_connected())

    def _reset_operation_range(self):
        """Resets the operation range to the stage range,
        then returns the max and min values.

        Returns:
            (float, float): max and min tuple
        """
        s_max, s_min = self._controller.get_stage_range()
        self._controller.set_operation_range(s_max, s_min)
        max, min = self._controller.get_operation_range()
        self.assertEqual(max, s_max)
        self.assertEqual(min, s_min)
        return max, min

    def _reset_cooling_heating(self):
        """Reset cooling/heating mode to Heating & Cooling
        """
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.HEATING_AND_COOLING)

    def _create_temp_range(self, max: float, min: float):
        """Creates a range from the min to max temperature, with
        STEP_COUNT steps, or with a step size of STEP_SIZE, if
        STEP_SIZE is not None.

        Args:
            max (float): maximum temperature value
            min (float): minimum temperature value

        Returns:
            range: Range object from min to max value, and STEP_COUNT steps
        """
        step = int((max - min) / self.STEP_COUNT
                   if self.STEP_SIZE is None else self.STEP_SIZE)
        return range(int(min), int(max), step)

    def _create_power_range(self, max, min):
        """Creates a range from the min to max power value, with
        STEP_COUNT steps, or with a step size of STEP_SIZE, if
        STEP_SIZE is not None.

        Args:
            max (float): maximum power value
            min (float): minimum power value

        Returns:
            range: Range object from min to max value, and STEP_COUNT steps
        """
        max = int(max * 100)
        min = int(min * 100)
        step = int(max - min / self.STEP_COUNT
                   if self.STEP_SIZE is None else self.STEP_SIZE)
        return range(min, max, step)
