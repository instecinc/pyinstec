"""Profile test cases for generating and running profiles.
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


class profile_test(controller_test):
    def setUp(self):
        """Set up controller and complete basic reset and testing of profile
        before execution.
        """

        # Call setUp of controller_test
        super().setUp()

        # Set to Cooling & Heating mode
        self._reset_cooling_heating()

        # Set operation range to stage range
        self._reset_operation_range()

        # Stop any currently running profiles
        self._controller.stop_profile()

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check profile status is stopped
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.STOP)

        # Clear test profile
        self._controller.delete_profile(self.TEST_PROFILE)

        # Confirm profile is cleared
        self.assertEqual(
            self._controller.get_profile_item_count(self.TEST_PROFILE), 0)

    def tearDown(self):
        """Reset testing profile and shut down controller.
        """

        # Clear test profile
        self._controller.delete_profile(self.TEST_PROFILE)

        # Confirm profile is cleared
        self.assertEqual(
            self._controller.get_profile_item_count(self.TEST_PROFILE), 0)

        # Call tearDown of controller_test
        super().tearDown()

    def test_run_profile(self):
        """Test profile runtime commands such as
        start, pause, resume, and stop.
        """

        # Add change to Heating & Cooling to profile
        self._controller.add_profile_item(
            self.TEST_PROFILE, instec.profile_item.HEATING_AND_COOLING)

        # Add 10 minute wait to profile
        self._controller.add_profile_item(
            self.TEST_PROFILE, instec.profile_item.WAIT, 10)

        # Start the profile
        self._controller.start_profile(self.TEST_PROFILE)

        # Delay for updated info and first instruction execution
        time.sleep(self.UPDATE_DELAY + 1)

        # Check profile status is running correct profile and index
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.RUN)
        self.assertEqual(status[1], self.TEST_PROFILE)
        self.assertEqual(status[2], 1)

        # Pause the profile
        self._controller.pause_profile()

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check profile status is running correct profile and index
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.PAUSE)
        self.assertEqual(status[1], self.TEST_PROFILE)
        self.assertEqual(status[2], 1)

        # Resume the profile
        self._controller.resume_profile()

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check profile status is running correct profile and index
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.RUN)
        self.assertEqual(status[1], self.TEST_PROFILE)
        self.assertEqual(status[2], 1)

        # Stop the profile
        self._controller.stop_profile()

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check profile status is running correct profile and index
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.STOP)
        self.assertEqual(status[1], self.TEST_PROFILE)
        self.assertEqual(status[2], 2)

    def test_profile_items(self):
        """Test adding all item instruction types, as well as set and
        delete item functionalities.
        """

        # Below setup is equivalent to:
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.HEATING_ONLY)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.COOLING_ONLY)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE,instec.profile_item.HEATING_AND_COOLING)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.HOLD, 50.0)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.RAMP, 60.0, 2.0)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE,instec.profile_item.LOOP_BEGIN, 4)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.HOLD, 20.0)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.HOLD, 40.0)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.STOP)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.LOOP_END)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.RPP, 0.4)
        # self._controller.add_profile_item(
        #     self.TEST_PROFILE, instec.profile_item.WAIT, 1)

        # List of item instruction numbers
        items = [9, 11, 8, 1, 3, 2, 3, 4, 1, 3, 1, 3, 7, 3, 5, 10, 3]

        # Corresponding parameters for each item
        b1 = {
            3: 50.0,
            4: 1,
            5: 60.0,
            6: 1,
            7: 4,
            8: 20.0,
            9: 1,
            10: 40.0,
            11: 1,
            13: 1,
            15: 0.4,
            16: 1
        }
        b2 = {
            5: 2.0
        }

        # Add each item into the profile
        for i in range(len(items)):
            self._controller.add_profile_item(
                self.TEST_PROFILE, instec.profile_item(items[i]),
                b1.get(i), b2.get(i))

        # Delay for updated info
        time.sleep(self.UPDATE_DELAY)

        # Check profile item count is correct
        self.assertEqual(
            self._controller.get_profile_item_count(self.TEST_PROFILE),
            len(items))

        # Check each item added properly
        for i in range(len(items)):
            # Check item instruction type
            item = self._controller.get_profile_item(self.TEST_PROFILE, i)
            self.assertEqual(item[0].value, items[i])

            # Check parameter 1 type, if applicable
            p1 = b1.get(i)
            self.assertEqual(item[1], p1)

            # Check parameter 2 type, if applicable
            p2 = b2.get(i)
            self.assertEqual(item[2], p2)

        # Test setting items by replacing every item with STOP
        for i in range(len(items)):
            # Set profile item at index i to STOP
            self._controller.set_profile_item(
                self.TEST_PROFILE, i, instec.profile_item.STOP)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check if profile item at index i is STOP
            item = self._controller.get_profile_item(self.TEST_PROFILE, i)
            self.assertEqual(item[0], instec.profile_item.STOP)

        # Test deleting items by removing every item
        for i in reversed(range(len(items))):
            # Delete item at index i
            self._controller.delete_profile_item(self.TEST_PROFILE, i)

            # Delay for updated info
            time.sleep(self.UPDATE_DELAY)

            # Check if number of items in profile is correct
            self.assertEqual(
                self._controller.get_profile_item_count(self.TEST_PROFILE), i)


if __name__ == '__main__':
    unittest.main()
