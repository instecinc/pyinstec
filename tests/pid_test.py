"""PID test cases to confirm PID functionality.
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


class pid_test(controller_test):
    def test_current_pid(self):
        """Tests functionality related to the get_current_pid()
        function. Confirms the correct values are returned when
        the function is called.
        """

        # Set to Cooling & Heating mode
        self._reset_cooling_heating()

        # Set operation range to stage range
        max, min = self._reset_operation_range()

        # See controller_test.py for more info on _create_temp_range
        for tsp in self._create_temp_range(max, min):
            # Execute HOLD command on controller at TSP,
            # so CSP is equal to TSP
            self._controller.hold(tsp)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Get the current PID value
            current = self._controller.get_current_pid()

            # Determine PID table used based on Heating or Cooling
            pid_table_type = None
            if self._controller.get_process_variables()[
                    self._controller.get_operating_slave() - 1] < tsp:
                pid_table_type = instec.pid_table.HEATING_HNC
            else:
                pid_table_type = instec.pid_table.COOLING_HNC

            # Initialize calculated PID variables
            p = None
            i = None
            d = None

            # If CSP is less than the minimum PID temperature value,
            # Set to minimum PID.
            pid_table = self._controller.get_pid(pid_table_type, 7)
            if tsp < pid_table[2]:
                p = pid_table[3]
                i = pid_table[4]
                d = pid_table[5]

            # If CSP is greater than the maximum PID temperature value,
            # Set to maximum PID.
            pid_table = self._controller.get_pid(pid_table_type, 0)
            if tsp > pid_table[2]:
                p = pid_table[3]
                i = pid_table[4]
                d = pid_table[5]

            # Otherwise, calculate PID by finding closest upper and lower bound
            # temperatures to CSP
            if p is None and i is None and d is None:
                # Find index with temperature closest to CSP
                index = 1
                while self._controller.get_pid(pid_table_type, index)[2] > tsp:
                    index += 1

                # Get PID entries
                entry_1 = self._controller.get_pid(pid_table_type, index - 1)
                entry_2 = self._controller.get_pid(pid_table_type, index)

                # Calculate current PID values
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

            # Compare calculated current PID values
            # to actual current PID values
            # May be slightly off due to rounding errors
            self.assertAlmostEqual(
                current[0], p, None, "Not close enough", 0.1)
            self.assertAlmostEqual(
                current[1], i, None, "Not close enough", 0.1)
            self.assertAlmostEqual(
                current[2], d, None, "Not close enough", 0.1)

            # Stop the current HOLD command
            self._controller.stop()

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

    def test_get_pid_invalid(self):
        """Tests functionality related to the get_pid()
        function. Confirms that exceptions are raised when
        invalid indices are passed.
        """

        # Get Invalid PID table entry at index -1
        try:
            self._controller.get_pid(
                instec.pid_table(0), -1)
            self.fail("Function did not raise exception when index = -1")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Get Invalid PID table entry at index 8
        try:
            self._controller.get_pid(
                instec.pid_table(0), 8)
            self.fail("Function did not raise exception when index = 8")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

    def test_set_pid_valid(self):
        """Tests functionality related to the set_current_pid()
        function. Confirms the functionality of setting PID
        values.
        """

        # Iterate through all PID tables and entries
        for pid_table_type in range(4):
            for index in range(8):
                # Get a valid PID table entry
                pid_table = self._controller.get_pid(
                    instec.pid_table(pid_table_type),
                    index)

                # Modify values to the original value + 1
                self._controller.set_pid(
                    instec.pid_table(pid_table_type),
                    index,
                    pid_table[2],
                    pid_table[3] + 1,
                    pid_table[4] + 1,
                    pid_table[5] + 1)

                # Delay for updated info
                time.sleep(self.UPDATE_DELAY)

                # Get the PID values at the same index
                modified = self._controller.get_pid(
                    instec.pid_table(pid_table_type),
                    index)

                # Check if retrieved values are equal to
                # modified values set earlier,
                # subject to floating point inaccuracy
                self.assertAlmostEqual(
                    modified[3], pid_table[3] + 1,
                    None, "Not close enough", 0.1)
                self.assertAlmostEqual(
                    modified[4], pid_table[4] + 1,
                    None, "Not close enough", 0.1)
                self.assertAlmostEqual(
                    modified[5], pid_table[5] + 1,
                    None, "Not close enough", 0.1)

                # Reset PID values back to original values
                self._controller.set_pid(
                    instec.pid_table(pid_table_type),
                    index,
                    pid_table[2],
                    pid_table[3],
                    pid_table[4],
                    pid_table[5])

                # Delay for updated info
                time.sleep(self.UPDATE_DELAY)

                # Get the PID values at the same index
                original = self._controller.get_pid(
                    instec.pid_table(pid_table_type),
                    index)

                # Check if retrieved values are equal to
                # original values obtained earlier,
                # subject to floating point inaccuracy
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

    def test_set_pid_invalid(self):
        """Tests functionality related to the get_current_pid()
        function. Confirms that exceptions are raised when
        invalid indices or invalid PID values are passed.
        """

        # Set operation range to stage range
        max, min = self._reset_operation_range()

        # Set Invalid PID table entry at index 8
        try:
            self._controller.set_pid(
                instec.pid_table(0), 8, max, 1, 1, 1)
            self.fail("Function did not raise exception when index > 8")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry over maximum temperature
        try:
            self._controller.set_pid(
                instec.pid_table(0), 0, max + 1, 1, 1, 1)
            self.fail("Function did not raise exception when temp > max")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry under minimum temperature
        try:
            self._controller.set_pid(
                instec.pid_table(0), 0, min - 1, 1, 1, 1)
            self.fail("Function did not raise exception when temp < min")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry with P below 0
        try:
            self._controller.set_pid(
                instec.pid_table(0), 0, max, -1, 1, 1)
            self.fail("Function did not raise exception when P < 0")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry with I below 0
        try:
            self._controller.set_pid(
                instec.pid_table(0), 0, max, 1, -1, 1)
            self.fail("Function did not raise exception when I < 0")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))

        # Set Invalid PID table entry with D below 0
        try:
            self._controller.set_pid(
                instec.pid_table(0), 0, max, 1, 1, -1)
            self.fail("Function did not raise exception when D < 0")
        except Exception as error:
            self.assertTrue(isinstance(error, ValueError))


if __name__ == '__main__':
    unittest.main()
