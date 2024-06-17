"""Various temperature command test cases.
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


class info_query_test(controller_test):
    def test_system_info(self):
        """Test retrieving system info.
        """

        # Get system info
        info = self._controller.get_system_information()

        # Check serial number
        self.assertEqual(info[2], self._controller.get_serial_number())

    def test_rtin(self):
        """Test retrieving runtime info.
        """

        # Set to Cooling & Heating mode
        self._reset_cooling_heating()

        # Set operation range to stage range
        max, min = self._reset_operation_range()

        # See controller_test.py for more info on _create_temp_range
        for tsp in self._create_temp_range(max, min):
            # Execute a RAMP command to set TSP and RT
            self._controller.ramp(tsp, self.RT)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Execute a HOLD command to set TSP and CSP
            self._controller.hold(tsp)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Execute a STOP command
            self._controller.stop()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Retrieve runtime information
            data = self._controller.get_runtime_information()

            # Retrieve current PP
            pp = self._controller.get_power()

            # Retrieve current PV
            pv = self._controller.get_process_variable()

            # Retrieve current MV
            mv = self._controller.get_monitor_value()

            # Check operating slave
            self.assertEqual(data[0], self._controller.get_operating_slave())

            # Check process variable
            # value may be slightly different due to command call delay
            self.assertAlmostEqual(
                data[1], pv, None, 'Not close enough', 0.1)

            # Check monitor value
            # value may be slightly different due to command call delay
            self.assertAlmostEqual(
                data[2], mv, None, 'Not close enough', 0.1)

            # Check TSP
            self.assertEqual(data[3], tsp)
            self.assertEqual(
                data[3], self._controller.get_set_point_temperature())

            # Check CSP
            self.assertEqual(data[4], tsp)

            # Check RT
            self.assertEqual(data[5], self.RT)
            self.assertEqual(data[5], self._controller.get_ramp_rate())

            # Check PP
            self.assertTrue(isinstance(data[6], float))
            self.assertEqual(data[6], pp)

            # Check system status
            self.assertEqual(data[7], instec.system_status.STOP)
            self.assertEqual(data[7], self._controller.get_system_status())

            # Check profile status
            self.assertEqual(data[8], instec.profile_status.STOP)

            # Check error status
            self.assertEqual(data[11], self._controller.get_error())

            # Delay so rtin gets updated info
            time.sleep(self.UPDATE_DELAY)

    def test_query(self):
        """Tests return values of various query commands.
        """

        # Get protection sensor temperature values
        try:
            ps = self._controller.get_protection_sensors()
            self.assertTrue(isinstance(ps, tuple))
        except Exception as error:
            self.fail(f'''Unwanted Exception getting
                      protection sensor temperature: {error}''')

        # Get powerboard temperature value
        try:
            pb = self._controller.get_powerboard_temperature()
            self.assertTrue(isinstance(pb, float))
        except Exception as error:
            self.fail(f'''Unwanted Exception getting
                      powerboard temperature: {error}''')

        # Get PV unit type
        try:
            pvu = self._controller.get_pv_unit_type()
            self.assertTrue(isinstance(pvu, instec.unit))
        except Exception as error:
            self.fail(f'''Unwanted Exception getting
                      PV unit type: {error}''')

        # Get MV unit type
        try:
            mvu = self._controller.get_mv_unit_type()
            self.assertTrue(isinstance(mvu, instec.unit))
        except Exception as error:
            self.fail(f'''Unwanted Exception getting
                      MV unit type: {error}''')

        # Get precision values of PV and MV
        try:
            precision = self._controller.get_precision()
            self.assertTrue(isinstance(precision, tuple)
                            and list(map(type, precision)) == [int, int])
        except Exception as error:
            self.fail(f'''Unwanted Exception getting
                      precision: {error}''')

    def test_valid_slave(self):
        """Test setting valid operating slave.
        """

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

        self._controller.set_operating_slave(op_slave)

    def test_invalid_slave(self):
        """Test setting invalid operating slave.
        """

        # Invalid slave number
        try:
            invalid_slave = self._controller.get_slave_count() + 1
            self._controller.set_operating_slave(invalid_slave)
            self.fail(f'''Function did not raise exception when
                      setting operating slave to {invalid_slave}''')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Invalid slave number
        try:
            self._controller.set_operating_slave(0)
            self.fail('''Function did not raise exception when
                      setting operating slave to 0''')
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))


class cooling_heating_test(controller_test):
    """Test setting various cooling/heating modes.
    """

    def test_cooling_only(self):
        """Test setting mode to Cooling Only.
        """

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

    def test_heating_and_cooling(self):
        """Test setting mode to Heating and Cooling.
        """

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

    def test_heating_only(self):
        """Test setting mode to Heating Only.
        """

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


class operation_range_test(controller_test):
    """Test setting various operation ranges.
    """

    def test_valid_operation_range(self):
        """Test setting valid operation range.
        """

        # Get stage range
        max, min = self._controller.get_stage_range()

        # Set valid operation range
        self._controller.set_operation_range(max, min)

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Get operation range
        omax, omin = self._controller.get_operation_range()

        # Check if range is set properly
        self.assertEqual(omax, max)
        self.assertEqual(omin, min)

    def test_invalid_operation_range(self):
        """Test setting invalid operation range.
        """

        # Get stage range
        max, min = self._controller.get_stage_range()

        # Try to set max out of stage range
        try:
            self._controller.set_operation_range(max + 1, min)
            self.fail("Function did not raise exception when max is too large")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Try to set min out of stage range
        try:
            self._controller.set_operation_range(max, min - 1)
            self.fail("Function did not raise exception when min is too small")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Try to set min > max
        try:
            self._controller.set_operation_range(min, max)
            self.fail("Function did not raise exception when max < min")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

    def test_default_operation_range(self):
        """Test default operation range validity.
        """

        # Get stage range
        max, min = self._controller.get_stage_range()

        # Get default stage range
        dmax, dmin = self._controller.get_default_operation_range()

        # Check if default range is within stage range
        self.assertLessEqual(dmax, max)
        self.assertGreaterEqual(dmin, min)


if __name__ == '__main__':
    unittest.main()
