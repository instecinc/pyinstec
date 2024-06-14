import instec
import time
import unittest
from controller_test import controller_test


class pid_test(controller_test):
    def test_pid(self):

        self._reset_cooling_heating()

        max, min = self._reset_operation_range()
        for tsp in self._create_temp_range(max, min):
            self._controller.hold(tsp)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            current = self._controller.get_current_pid()
            mode = self._controller.get_cooling_heating_status()
            # Determine PID table used
            pid_table_type = None
            if mode == instec.temperature_mode.COOLING_ONLY:
                pid_table_type = instec.pid_table.COOLING_CO
            elif mode == instec.temperature_mode.HEATING_ONLY:
                pid_table_type = instec.pid_table.HEATING_HO
            else:
                if self._controller.get_process_variables()[
                        self._controller.get_operating_slave() - 1] < tsp:
                    pid_table_type = instec.pid_table.HEATING_HNC
                else:
                    pid_table_type = instec.pid_table.COOLING_HNC

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
            time.sleep(self.UPDATE_DELAY)

        for pid_table_type in range(4):
            for index in range(8):
                # Get a valid PID table entry
                pid_table = self._controller.get_pid(
                    instec.pid_table(pid_table_type),
                    index)

                # Modify values
                self._controller.set_pid(
                    instec.pid_table(pid_table_type),
                    index,
                    pid_table[2],
                    pid_table[3] + 1,
                    pid_table[4] + 1,
                    pid_table[5] + 1)

                # Delay for updated info
                time.sleep(self.UPDATE_DELAY)

                modified = self._controller.get_pid(
                    instec.pid_table(pid_table_type),
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
                    instec.pid_table(pid_table_type),
                    index,
                    pid_table[2],
                    pid_table[3],
                    pid_table[4],
                    pid_table[5])

                # Delay for updated info
                time.sleep(self.UPDATE_DELAY)

                original = self._controller.get_pid(
                    instec.pid_table(pid_table_type),
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
                time.sleep(self.UPDATE_DELAY)

        # Get Invalid PID table entry
        try:
            pid_table = self._controller.get_pid(
                instec.pid_table(0), 8)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.pid_table(0), 8, max, 1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.pid_table(0), 0, max + 1, 1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.pid_table(0), 0, min - 1, 1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.pid_table(0), 0, max, -1, 1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.pid_table(0), 0, max, 1, -1, 1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry
        try:
            pid_table = self._controller.set_pid(
                instec.pid_table(0), 0, max, 1, 1, -1)
            self.fail("Function did not raise exception")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))


if __name__ == '__main__':
    unittest.main()
