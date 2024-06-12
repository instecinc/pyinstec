import unittest
import time
import instec

mode = instec.mode.ETHERNET
baud = 38400
port = 'COM3'

UPDATE_DELAY = 0.2   # in seconds, so queries don't read old values
STEP_COUNT = 8       # Number of steps for each TSP loop
RAMP = 5


class temperature_test(unittest.TestCase):
    def setUp(self):
        self._initialize_controller()

    def tearDown(self):
        self._shutdown_controller()

    def _initialize_controller(self):
        # Initialize and connect to controller
        self._controller = instec.instec(mode, baud, port)
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

    def test_rtin(self):

        max, min = self._reset_operation_range()
        for tsp in range(int(min), int(max), int((max - min) / STEP_COUNT)):
            self._controller.ramp(tsp, RAMP)
            self._controller.hold(tsp)
            self._controller.stop()

            # Delay so rtin gets updated info
            time.sleep(UPDATE_DELAY)

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
            self.assertEqual(data[5], RAMP)
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
            time.sleep(UPDATE_DELAY)

    def test_hold(self):

        self._reset_cooling_heating()

        max, min = self._reset_operation_range()
        for tsp in range(int(min), int(max), int((max - min) / STEP_COUNT)):
            # Set valid hold
            self._controller.hold(tsp)

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

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
            time.sleep(UPDATE_DELAY)

            # Check system status
            self.assertAlmostEqual(
                self._controller.get_set_point_temperature(),
                tsp, None, "Not close enough", 0.1)
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.STOP)

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

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
        for tsp in range(int(min), int(max), int((max - min) / STEP_COUNT)):
            start_temp = self._controller.get_process_variables()[
                self._controller.get_operating_slave() - 1]
            self._controller.ramp(tsp, RAMP)
            # Start time and temperature at beginning of ramp
            start_time = time.time()

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

            # Check system TSP and status
            data = self._controller.get_runtime_information()
            self.assertAlmostEqual(
                data[4],
                start_temp + (-1 if start_temp > tsp else 1)
                * ((time.time() - start_time) / 60 * RAMP),
                None, "Not close", 0.5)
            self.assertEqual(data[3], tsp)
            self.assertEqual(data[5], RAMP)
            self.assertEqual(data[7], instec.system_status.RAMP)

            # Stop ramp
            self._controller.stop()

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

            # Check system status
            data = self._controller.get_runtime_information()
            self.assertEqual(data[3], tsp)
            self.assertEqual(data[5], RAMP)
            self.assertEqual(data[7], instec.system_status.STOP)

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

        # Set invalid ramp tsp
        try:
            self._controller.ramp(max + 1, RAMP)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid ramp tsp
        try:
            self._controller.ramp(min - 1, RAMP)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Get range of ramp values
        ramp_range = self._controller.get_ramp_rate_range()
        ramp_max = ramp_range[0]
        ramp_min = ramp_range[1]

        # Set invalid ramp rate
        self._controller.ramp(max, ramp_max + 1)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Check ramp rate
        self.assertEqual(self._controller.get_ramp_rate(), ramp_max)

        # Stop ramp
        self._controller.stop()

        # Set invalid ramp rate
        self._controller.ramp(max, ramp_min - 1)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Check ramp rate
        self.assertEqual(self._controller.get_ramp_rate(), ramp_min)

        # Stop ramp
        self._controller.stop()

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

    def test_rpp(self):

        self._reset_cooling_heating()

        self._reset_operation_range()
        for pp in range(-100, 100, int(200 / STEP_COUNT)):
            # Set valid rpp
            self._controller.rpp(pp / 100.0)

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

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
            time.sleep(UPDATE_DELAY)

            # Check system status
            self.assertAlmostEqual(
                self._controller.get_power(),
                0, None, "Not close enough", 0.1)
            self.assertEqual(
                self._controller.get_system_status(),
                instec.system_status.STOP)

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

        # Set invalid rpp
        try:
            self._controller.rpp(1.1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set invalid rpp
        try:
            self._controller.rpp(-1.1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

    def test_pid(self):

        self._reset_cooling_heating()

        max, min = self._reset_operation_range()
        for tsp in range(int(min), int(max), int((max - min) / STEP_COUNT)):
            self._controller.hold(tsp)

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

            current = self._controller.get_current_pid()
            cooling_heating_mode = self._controller.get_cooling_heating_status()
            # Determine PID table used
            pid_table_type = None
            if cooling_heating_mode == instec.temperature_mode.COOLING_ONLY:
                pid_table_type = instec.PID_table.COOLING_CO
            elif cooling_heating_mode == instec.temperature_mode.HEATING_ONLY:
                pid_table_type = instec.PID_table.HEATING_HO
            else:
                if self._controller.get_process_variables()[
                        self._controller.get_operating_slave() - 1] < tsp:
                    pid_table_type = instec.PID_table.HEATING_HNC
                else:
                    pid_table_type = instec.PID_table.COOLING_HNC

            p = None
            i = None
            d = None

            pid_table = self._controller.get_pid(pid_table_type, 7)
            if tsp < pid_table[2]:
                p = pid_table[3]
                i = pid_table[4]
                d = pid_table[5]

            pid_table = self._controller.get_pid(pid_table_type, 0)
            if tsp > pid_table[2]:
                p = pid_table[3]
                i = pid_table[4]
                d = pid_table[5]

            if p is None and i is None and d is None:
                index = 1
                while self._controller.get_pid(pid_table_type, index)[2] > tsp:
                    index += 1
                entry_1 = self._controller.get_pid(pid_table_type, index - 1)
                entry_2 = self._controller.get_pid(pid_table_type, index)
                p = ((entry_1[3] - entry_2[3])
                     * (tsp - entry_2[2])
                     / (entry_1[2] - entry_2[2])
                     + entry_2[3])
                i = ((entry_1[4] - entry_2[4])
                     * (tsp - entry_2[2])
                     / (entry_1[2] - entry_2[2])
                     + entry_2[4])
                d = ((entry_1[5] - entry_2[5])
                     * (tsp - entry_2[2])
                     / (entry_1[2] - entry_2[2])
                     + entry_2[5])

            # May be slightly off due to rounding errors
            self.assertAlmostEqual(
                current[0], p, None, "Not close enough", 0.1)
            self.assertAlmostEqual(
                current[1], i, None, "Not close enough", 0.1)
            self.assertAlmostEqual(
                current[2], d, None, "Not close enough", 0.1)

            self._controller.stop()

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

        for pid_table_type in range(4):
            for index in range(8):
                # Get a valid PID table entry
                pid_table = self._controller.get_pid(
                    instec.PID_table(pid_table_type),
                    index)

                # Modify values
                self._controller.set_pid(
                    instec.PID_table(pid_table_type),
                    index,
                    pid_table[2],
                    pid_table[3] + 1,
                    pid_table[4] + 1,
                    pid_table[5] + 1)

                # Delay for updated info
                time.sleep(UPDATE_DELAY)

                modified = self._controller.get_pid(
                    instec.PID_table(pid_table_type),
                    index)

                # Floating point inaccuracy
                self.assertAlmostEqual(
                    modified[3], pid_table[3] + 1,
                    None, "Not close enough", 0.1)
                self.assertAlmostEqual(
                    modified[4], pid_table[4] + 1,
                    None, "Not close enough", 0.1)
                self.assertAlmostEqual(
                    modified[5], pid_table[5] + 1,
                    None, "Not close enough", 0.1)

                # Reset values
                self._controller.set_pid(
                    instec.PID_table(pid_table_type),
                    index,
                    pid_table[2],
                    pid_table[3],
                    pid_table[4],
                    pid_table[5])

                # Delay for updated info
                time.sleep(UPDATE_DELAY)

                original = self._controller.get_pid(
                    instec.PID_table(pid_table_type),
                    index)

                # Floating point inaccuracy
                self.assertAlmostEqual(
                    original[3], pid_table[3],
                    None, "Not close enough", 0.1)
                self.assertAlmostEqual(
                    original[4], pid_table[4],
                    None, "Not close enough", 0.1)
                self.assertAlmostEqual(
                    original[5], pid_table[5],
                    None, "Not close enough", 0.1)

                # Delay for updated info
                time.sleep(UPDATE_DELAY)

        # Get Invalid PID table entry
        try:
            pid_table = self._controller.get_pid(
                instec.PID_table(0), 8)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.PID_table(0), 8, max, 1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.PID_table(0), 0, max + 1, 1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.PID_table(0), 0, min - 1, 1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.PID_table(0), 0, max, -1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.PID_table(0), 0, max, 1, -1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.PID_table(0), 0, max, 1, 1, -1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

    def test_cooling_heating(self):

        # Set status
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.COOLING_ONLY)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Check status
        self.assertEqual(self._controller.get_cooling_heating_status(),
                         instec.temperature_mode.COOLING_ONLY)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Set status
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.HEATING_AND_COOLING)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Check status
        self.assertEqual(self._controller.get_cooling_heating_status(),
                         instec.temperature_mode.HEATING_AND_COOLING)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Set status
        self._controller.set_cooling_heating_status(
            instec.temperature_mode.HEATING_ONLY)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

        # Check status
        self.assertEqual(self._controller.get_cooling_heating_status(),
                         instec.temperature_mode.HEATING_ONLY)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

    def test_operation_range(self):

        stage_range = self._controller.get_stage_range()
        max = stage_range[0]
        min = stage_range[1]

        # Set valid range
        self._controller.set_operation_range(max, min)

        # Delay for updated info
        time.sleep(UPDATE_DELAY)

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
            time.sleep(UPDATE_DELAY)

            # Check operating slave
            self.assertTrue(self._controller.get_operating_slave(), i + 1)

            # Delay for updated info
            time.sleep(UPDATE_DELAY)

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
