""" Temperature control test cases for functions such as
HOLD, RAMP, or RPP.
See controller_test.py first before running this test.
"""


import time
import unittest
import sys
import os

# Run tests using local copy of library - comment this out if unnecessary
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import instec
from controller_test import controller_test


class hold_test(controller_test):
    """Test various parameters for the HOLD command.
    """

    def test_hold_valid(self):
        """Test valid HOLD values.
        """

        # Set to Cooling & Heating mode
        self._reset_cooling_heating()

        # Set operation range to stage range
        max, min = self._reset_operation_range()

        # Iterate through range of TSP values
        for tsp in self._create_temp_range(max, min):
            # Set valid HOLD
            self._controller.hold(tsp)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check if TSP is correct
            self.assertAlmostEqual(
                self._controller.get_set_point_temperature(),
                tsp, None, 'Not close enough', 0.1)

            # Check if system status is HOLD
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.HOLD)

            # Stop HOLD
            self._controller.stop()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check if TSP is correct
            self.assertAlmostEqual(
                self._controller.get_set_point_temperature(),
                tsp, None, 'Not close enough', 0.1)

            # Check if system status is STOP
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.STOP)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

    def test_hold_invalid(self):
        """Test invalid HOLD values.
        """

        # Set invalid hold
        try:
            self._controller.hold(max + 1)
            self.fail('Function did not raise exception when tsp > max')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid hold
        try:
            self._controller.hold(min - 1)
            self.fail('Function did not raise exception when tsp < min')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))


class ramp_test(controller_test):
    """Test various parameters for the RAMP command.
    """

    def test_ramp_tsp_valid(self):
        """Test valid TSP values.
        """

        # Set to Cooling & Heating mode
        self._reset_cooling_heating()

        # Set operation range to stage range
        max, min = self._reset_operation_range()

        # Iterate through range of TSP values
        for tsp in self._create_temp_range(max, min):

            # Get current PV value
            start_temp = self._controller.get_process_variable()

            # Set valid RAMP
            self._controller.ramp(tsp, self.RT)

            # Start time at beginning of RAMP
            start_time = time.time()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Get runtime info
            data = self._controller.get_runtime_information()

            # Check if CSP is as expected
            self.assertAlmostEqual(
                data[4],
                start_temp + (-1 if start_temp > tsp else 1)
                * ((time.time() - start_time) / 60 * self.RT),
                None, 'Not close', 0.5)

            # Check if TSP is correct
            self.assertEqual(data[3], tsp)

            # Check if RT is correct
            self.assertEqual(data[5], self.RT)

            # Check if system status is RAMP
            self.assertEqual(data[7], instec.system_status.RAMP)

            # Stop ramp
            self._controller.stop()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Get runtime info
            data = self._controller.get_runtime_information()

            # Check if TSP is correct
            self.assertEqual(data[3], tsp)

            # Check if RT is correct
            self.assertEqual(data[5], self.RT)

            # Check if system status is STOP
            self.assertEqual(data[7], instec.system_status.STOP)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

    def test_ramp_tsp_invalid(self):
        """Test invalid TSP values.
        """

        # Set invalid ramp tsp
        try:
            self._controller.ramp(max + 1, self.RT)
            self.fail('Function did not raise exception')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid ramp tsp
        try:
            self._controller.ramp(min - 1, self.RT)
            self.fail('Function did not raise exception')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

    def test_ramp_rt_invalid(self):
        """Test invalid RT values.
        """

        # Get range of ramp values
        ramp_range = self._controller.get_ramp_rate_range()
        max = ramp_range[0]
        min = ramp_range[1]

        # Get current PV
        pv = self._controller.get_process_variable()

        # Set invalid ramp rate
        try:
            self._controller.ramp(pv, max + 1)
            self.fail('Function did not raise exception when rt > max')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid ramp rate
        try:
            self._controller.ramp(pv, min - 1)
            self.fail('Function did not raise exception when rt < min')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))


class rpp_test(controller_test):
    """Test various parameters for the RPP command.
    """

    def test_rpp_valid(self):
        """Test valid PP values.
        """

        # Set to Cooling & Heating mode
        self._reset_cooling_heating()

        # Iterate through cooling/heating modes
        for i in range(3):
            # Set cooling/heating mode
            self._controller.set_cooling_heating_status(
                instec.temperature_mode(i))

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Get power range
            max, min = self._controller.get_power_range()

            # Iterate through range of PP values
            for pp in self._create_power_range(max, min):
                # Set valid rpp
                self._controller.rpp(pp / 100.0)

                # Delay for updated info
                time.sleep(self.UPDATE_DELAY)

                # Check if PP is correct
                self.assertAlmostEqual(
                    self._controller.get_power(),
                    pp / 100.0, None, 'Not close enough', 0.1)

                # Check if system status is RPP
                self.assertEqual(
                    self._controller.get_system_status(),
                    instec.system_status.RPP)

                # Stop rpp
                self._controller.stop()

                # Delay for updated info
                time.sleep(self.UPDATE_DELAY)

                # Check if PP is correct
                self.assertAlmostEqual(
                    self._controller.get_power(),
                    0, None, 'Not close enough', 0.1)

                # Check if system status is STOP
                self.assertEqual(
                    self._controller.get_system_status(),
                    instec.system_status.STOP)

                # Delay for updated info
                time.sleep(self.UPDATE_DELAY)

    def test_rpp_invalid(self):
        """Test invalid PP values.
        """

        # Set invalid rpp
        try:
            self._controller.rpp(max + 0.1)
            self.fail('Function did not raise exception')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid rpp
        try:
            self._controller.rpp(min - 0.1)
            self.fail('Function did not raise exception')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))


if __name__ == '__main__':
    unittest.main()
