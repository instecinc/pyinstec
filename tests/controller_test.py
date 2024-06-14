"""controller_test.py defines helper functions for all
other tests.
"""


import unittest
import instec


class controller_test(unittest.TestCase):
    MODE = instec.mode.USB
    BAUD = 38400
    PORT = 'COM3'

    UPDATE_DELAY = 0.25   # in seconds, so queries don't read old values
    STEP_COUNT = 8       # Number of steps for each TSP loop
    RAMP = 5

    def setUp(self):
        """Called at the start of each test.
        """
        self._initialize_controller()

    def tearDown(self):
        """Called at the end of each test.
        """
        self._shutdown_controller()

    def _initialize_controller(self):
        # Initialize and connect to controller
        self._controller = instec.MK2000(self.MODE, self.BAUD, self.PORT)
        self._controller.connect()
        self.assertTrue(self._controller.is_connected())

    def _shutdown_controller(self):
        # Disconnect from controller
        self._controller.disconnect()
        self.assertFalse(self._controller.is_connected())

    def _reset_operation_range(self):
        # Reset operation range to stage range
        s_max, s_min = self._controller.get_stage_range()
        self._controller.set_operation_range(s_max, s_min)
        max, min = self._controller.get_operation_range()
        self.assertEqual(max, s_max)
        self.assertEqual(min, s_min)
        return max, min

    def _reset_cooling_heating(self):
        # Reset cooling/heating status to heating and cooling
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.HEATING_AND_COOLING)

    def _create_temp_range(self, max, min):
        step = int((max - min) / self.STEP_COUNT)
        return range(int(min), int(max), step)

    def _create_power_range(self, max, min):
        max = int(max * 100)
        min = int(min * 100)
        step = int(max - min / self.STEP_COUNT)
        return range(min, max, step)
