"""Comprehensive test for the instec library.
This test set runs every available non-profile function, and takes
roughly a minute to finish. The STEP_COUNT and UPDATE_DELAY variables
should be updated accordingly before running this test. STEP_COUNT adjusts
the number of steps certain tests take within the temperature range of the
stage, and UPDATE_DELAY accounts for how long the controller takes to
update values internally. If a test fails due to an assertion error, try
increasing the UPDATE_DELAY in case your controller takes longer to respond.
"""

import time
import instec
import unittest
from controller_test import controller_test


class temperature_test(controller_test):
    def test_rtin(self):
        max, min = self._reset_operation_range()
        for tsp in self._create_temp_range(max, min):
            self._controller.ramp(tsp, self.RAMP)
            self._controller.hold(tsp)
            self._controller.stop()

            # Delay so rtin gets updated info
            time.sleep(self.UPDATE_DELAY)

            data = self._controller.get_runtime_information()
            pv = self._controller.get_process_variables()
            mv = self._controller.get_monitor_values()

            # Check operating slave
            self.assertEqual(data[0], self._controller.get_operating_slave())
            # Check process variables
            # value may shift slightly between command calls
            self.assertAlmostEqual(
                data[1], pv[data[0] - 1], None, "Not close enough", 0.1)
            # Check monitor values
            # value may shift slightly between command calls
            self.assertAlmostEqual(
                data[2], mv[data[0] - 1], None, "Not close enough", 0.1)
            # Check TSP
            self.assertEqual(data[3], tsp)
            self.assertEqual(
                data[3], self._controller.get_set_point_temperature())
            # Check CSP
            self.assertEqual(data[4], tsp)
            # Check RT
            self.assertEqual(data[5], self.RAMP)
            self.assertEqual(data[5], self._controller.get_ramp_rate())
            # Check PP
            self.assertTrue(isinstance(data[6], float))
            self.assertEqual(data[6], self._controller.get_power())
            # Check system status
            self.assertEqual(data[7], instec.system_status.STOP)
            self.assertEqual(data[7], self._controller.get_system_status())
            # Check profile status
            self.assertEqual(data[8], instec.profile_status.STOP)
            # Check error status
            self.assertEqual(data[11], self._controller.get_error())

            # Delay so rtin gets updated info
            time.sleep(self.UPDATE_DELAY)

    def test_hold(self):

        self._reset_cooling_heating()

        max, min = self._reset_operation_range()
        for tsp in self._create_temp_range(max, min):
            # Set valid hold
            self._controller.hold(tsp)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check system TSP and status
            self.assertAlmostEqual(
                self._controller.get_set_point_temperature(),
                tsp, None, "Not close enough", 0.1)
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.HOLD)

            # Stop hold
            self._controller.stop()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check system status
            self.assertAlmostEqual(
                self._controller.get_set_point_temperature(),
                tsp, None, "Not close enough", 0.1)
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.STOP)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

        # Set invalid hold
        try:
            self._controller.hold(max + 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid hold
        try:
            self._controller.hold(min - 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

    def test_ramp(self):

        self._reset_cooling_heating()

        max, min = self._reset_operation_range()
        for tsp in self._create_temp_range(max, min):
            start_temp = self._controller.get_process_variables()[
                self._controller.get_operating_slave() - 1]
            self._controller.ramp(tsp, self.RAMP)
            # Start time and temperature at beginning of ramp
            start_time = time.time()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check system TSP and status
            data = self._controller.get_runtime_information()
            self.assertAlmostEqual(
                data[4],
                start_temp + (-1 if start_temp > tsp else 1)
                * ((time.time() - start_time) / 60 * self.RAMP),
                None, "Not close", 0.5)
            self.assertEqual(data[3], tsp)
            self.assertEqual(data[5], self.RAMP)
            self.assertEqual(data[7], instec.system_status.RAMP)

            # Stop ramp
            self._controller.stop()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check system status
            data = self._controller.get_runtime_information()
            self.assertEqual(data[3], tsp)
            self.assertEqual(data[5], self.RAMP)
            self.assertEqual(data[7], instec.system_status.STOP)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

        # Set invalid ramp tsp
        try:
            self._controller.ramp(max + 1, self.RAMP)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid ramp tsp
        try:
            self._controller.ramp(min - 1, self.RAMP)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Get range of ramp values
        ramp_range = self._controller.get_ramp_rate_range()
        ramp_max = ramp_range[0]
        ramp_min = ramp_range[1]

        # Set invalid ramp rate
        self._controller.ramp(max, ramp_max + 1)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check ramp rate
        self.assertEqual(self._controller.get_ramp_rate(), ramp_max)

        # Stop ramp
        self._controller.stop()

        # Set invalid ramp rate
        self._controller.ramp(max, ramp_min - 1)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check ramp rate
        self.assertEqual(self._controller.get_ramp_rate(), ramp_min)

        # Stop ramp
        self._controller.stop()

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

    def test_rpp(self):

        self._reset_cooling_heating()

        max, min = self._controller.get_power_range()
        for pp in self._create_power_range(max, min):
            # Set valid rpp
            self._controller.rpp(pp / 100.0)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check system TSP and status
            self.assertAlmostEqual(
                self._controller.get_power(),
                pp / 100.0, None, "Not close enough", 0.1)
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.PP)

            # Stop rpp
            self._controller.stop()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check system status
            self.assertAlmostEqual(
                self._controller.get_power(),
                0, None, "Not close enough", 0.1)
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.STOP)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

        # Set invalid rpp
        try:
            self._controller.rpp(max + 0.1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid rpp
        try:
            self._controller.rpp(min - 0.1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

    def test_cooling_heating(self):

        # Set status
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.COOLING_ONLY)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check status
        self.assertEqual(self._controller.get_cooling_heating_status(),
                         instec.temperature_mode.COOLING_ONLY)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Set status
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.HEATING_AND_COOLING)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check status
        self.assertEqual(self._controller.get_cooling_heating_status(),
                         instec.temperature_mode.HEATING_AND_COOLING)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Set status
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.HEATING_ONLY)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check status
        self.assertEqual(self._controller.get_cooling_heating_status(),
                         instec.temperature_mode.HEATING_ONLY)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

    def test_operation_range(self):

        stage_range = self._controller.get_stage_range()
        max = stage_range[0]
        min = stage_range[1]

        # Set valid range
        self._controller.set_operation_range(max, min)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check range
        op_range = self._controller.get_operation_range()
        self.assertEqual(op_range[0], max)
        self.assertEqual(op_range[1], min)

        # Get default stage range
        default_range = self._controller.get_default_operation_range()
        self.assertLessEqual(default_range[0], max)
        self.assertGreaterEqual(default_range[1], min)

    def test_system_info(self):

        # Get system info
        info = self._controller.get_system_information()

        # Check serial number
        self.assertEqual(info[2], self._controller.get_serial_number())

    def test_query(self):

        try:
            self._controller.get_protection_sensors()
        except Exception as error:
            self.fail(f"Unwanted Exception {error}")

        try:
            self._controller.get_powerboard_temperature()
        except Exception as error:
            self.fail(f"Unwanted Exception {error}")

        try:
            self._controller.get_pv_unit_type()
        except Exception as error:
            self.fail(f"Unwanted Exception {error}")

        try:
            self._controller.get_mv_unit_type()
        except Exception as error:
            self.fail(f"Unwanted Exception {error}")

        try:
            self._controller.get_precision()
        except Exception as error:
            self.fail(f"Unwanted Exception {error}")

    def test_slaves(self):

        # Get operating slave
        op_slave = self._controller.get_operating_slave()

        for i in range(self._controller.get_slave_count()):
            # Set operating slave
            self._controller.set_operating_slave(i + 1)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check operating slave
            self.assertTrue(self._controller.get_operating_slave(), i + 1)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

        # Invalid slave number
        try:
            self._controller.set_operating_slave(
                self._controller.get_slave_count() + 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Invalid slave number
        try:
            self._controller.set_operating_slave(0)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        self._controller.set_operating_slave(op_slave)


if __name__ == '__main__':
    unittest.main()
