"""Comprehensive profile test for instec library.
"""


import instec
import time
import unittest
from controller_test import controller_test


class profile_test(controller_test):
    def test_profile(self):
        self._reset_operation_range()
        self._reset_cooling_heating()
        self._controller.stop_profile()
        time.sleep(self.UPDATE_DELAY)
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.STOP)
        
        profile = 4

        self._controller.delete_profile(profile)
        
        # Equivalent to:
        # self._controller.add_profile_item(0, instec.profile_item.HEATING_ONLY)
        # self._controller.add_profile_item(0, instec.profile_item.COOLING_ONLY)
        # self._controller.add_profile_item(0, instec.profile_item.HEATING_AND_COOLING)
        # self._controller.add_profile_item(0, instec.profile_item.HOLD, 50.0)
        # self._controller.add_profile_item(0, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(0, instec.profile_item.RAMP, 60.0, 2.0)
        # self._controller.add_profile_item(0, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(0,instec.profile_item.LOOP_BEGIN, 4)
        # self._controller.add_profile_item(0, instec.profile_item.HOLD, 20.0)
        # self._controller.add_profile_item(0, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(0, instec.profile_item.HOLD, 40.0)
        # self._controller.add_profile_item(0, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(0, instec.profile_item.STOP)
        # self._controller.add_profile_item(0, instec.profile_item.WAIT, 1)
        # self._controller.add_profile_item(0, instec.profile_item.LOOP_END)
        # self._controller.add_profile_item(0, instec.profile_item.RPP, 0.4)
        # self._controller.add_profile_item(0, instec.profile_item.WAIT, 1)
        
        items = [9, 11, 8, 1, 3, 2, 3, 4, 1, 3, 1, 3, 7, 3, 5, 10, 3]
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

        for i in range(len(items)):
            self._controller.add_profile_item(profile, instec.profile_item(items[i]), b1.get(i), b2.get(i))

        for i in range(len(items)):
            item = self._controller.get_profile_item(profile, i)
            self.assertEqual(item[0].value, items[i])
            temp = b1.get(i)
            if temp is not None:
                self.assertEqual(item[1], temp)
            temp = b2.get(i)
            if temp is not None:
                self.assertEqual(item[2], temp)

        self._controller.set_profile_item(profile, 1, instec.profile_item.STOP)
        time.sleep(self.UPDATE_DELAY)
        item = self._controller.get_profile_item(profile, 1)
        self.assertEqual(item[0], instec.profile_item.STOP)

        self._controller.delete_profile_item(profile, 1)
        item = self._controller.get_profile_item(profile, 1)
        self.assertEqual(item[0], instec.profile_item.HEATING_AND_COOLING)

        self._controller.start_profile(profile)
        time.sleep(self.UPDATE_DELAY)
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.RUN)

        self._controller.pause_profile()
        time.sleep(self.UPDATE_DELAY)
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.PAUSE)

        self._controller.resume_profile()
        time.sleep(self.UPDATE_DELAY)
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.RUN)

        self._controller.stop_profile()
        time.sleep(self.UPDATE_DELAY)
        status = self._controller.get_profile_state()
        self.assertEqual(status[0], instec.profile_status.STOP)


if __name__ == '__main__':
    unittest.main()
