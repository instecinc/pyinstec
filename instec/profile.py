"""Command set for profile commands.
"""


from instec.command import command
from instec.constants import profile_status, profile_item
from instec.temperature import temperature


class profile(command):
    def get_profile_state(self):
        """Get the current profile state.
        p_status (profile_status):    Current profile execution status code
        p (int):            Active profile number
        i (int):            Current index of profile during execution

        Returns:
            (profile_status, int, int): Profile tuple
        """
        info = self._controller._send_command('PROF:RTST?').split(',')
        p_status = profile_status(info[0])
        p = int(info[1])
        i = int(info[2])

        return p_status, p, i

    def start_profile(self, p: int):
        """Start the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).

        Args:
            p (int): Selected profile
        """
        if p >= 0 and p < 5:
            self._controller._send_command(f'PROF:STAR {p}', False)
        else:
            raise ValueError('Invalid profile')

    def pause_profile(self):
        """Pauses the currently running profile, if applicable.
        This will allow the currently running instruction to
        finish, stopping before the next command.
        """
        self._controller._send_command('PROF:PAUS', False)

    def resume_profile(self):
        """Resumes the currently running profile, if applicable.
        """
        self._controller._send_command('PROF:RES', False)

    def stop_profile(self):
        """Stops the currently running/paused profile, if applicable.
        """
        self._controller._send_command('PROF:STOP', False)

    def delete_profile(self, p: int):
        """Delete the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).

        Args:
            p (int): Selected profile
        """
        if p >= 0 and p < 5:
            self._controller._send_command(f'PROF:EDIT:PDEL {p}', False)
        else:
            raise ValueError('Invalid profile')

    def delete_profile_item(self, p: int, i: int):
        """Delete the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).
        Items are zero-indexed, ranging from 0 to 255.

        Args:
            p (int): Selected profile
            i (int): Selected item index
        """
        if p >= 0 and p < 5:
            if i >= 0 and i < 255:
                self._controller._send_command(f'PROF:EDIT:PDEL {p},{i}', False)
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def insert_profile_item(self, p: int, i: int, item: profile_item,
                            b1: float=None, b2: float=None):
        """Insert the selected item into the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).
        Items are zero-indexed, ranging from 0 to 255.

        Args:
            p (int): Selected profile
            i (int): Selected item index
            item(profile_item): Item instruction type
        """
        if p >= 0 and p < 5:
            if i >= 0 and i < 255:
                match [item, b1, b2]:
                    case [profile_item.END | profile_item.LOOP_BEGIN
                           | profile_item.LOOP_END | profile_item.STOP
                           | profile_item.COOLING_ON
                           | profile_item.COOLING_OFF, None, None]:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},{item.value()}', False)
                    case [profile_item.HOLD, x,
                          None] if temperature.is_in_operation_range(x):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value()},{float(b1)}', False)
                    case [profile_item.RPP, x,
                          None] if temperature.is_in_power_range(x):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value()},{float(b1)}', False)
                    case [profile_item.WAIT, x,
                          None] if x >= 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value()},{float(b1)}', False)
                    case [profile_item.RAMP,
                          x, y] if (temperature.is_in_operation_range(x)
                                    and temperature.is_in_ramp_rate_range(y)):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value()},{float(b1)},{float(b2)}', False)
                    case [profile_item.PURGE,
                          x, y] if x >= 0.0 and y > 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value()},{float(b1)},{float(b2)}', False)
                    case _:
                        raise ValueError('Invalid item/parameters')
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')