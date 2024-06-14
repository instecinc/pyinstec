import instec
import time
import unittest
from controller_test import controller_test


class profile_test(controller_test):
    def test_profile(self):
        self._reset_operation_range()
        self._reset_cooling_heating()
        self._controller.stop_profile()

        status = self._controller.get_profile_state()
        self.assertEqual(status, [instec.profile_status.STOP, 0, 0])


if __name__ == '__main__':
    unittest.main()
