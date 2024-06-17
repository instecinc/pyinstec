"""Command set for profile commands.
"""


from instec.command import command
from instec.constants import profile_status, profile_item
from instec.temperature import temperature


class profile(command):
    """All profile related commands.
    """

    PROFILE_NUM = 5
    ITEM_NUM = 255

    def get_profile_state(self):
        """Get the current profile state.
        p_status (profile_status):    Current profile execution status code
        p (int):            Active profile number
        i (int):            Current index of profile during execution

        Returns:
            (profile_status, int, int): Profile tuple
        """
        info = self._controller._send_command('PROF:RTST?').split(',')
        p_status = profile_status(int(info[0]))
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
        if self.is_valid_profile(p):
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
        if self.is_valid_profile(p):
            self._controller._send_command(f'PROF:EDIT:PDEL {p}', False)
        else:
            raise ValueError('Invalid profile')

    def delete_profile_item(self, p: int, i: int):
        """Delete the selected profile item.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).
        Items are zero-indexed, ranging from 0 to 255.

        Args:
            p (int): Selected profile
            i (int): Selected item index
        """
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                self._controller._send_command(
                    f'PROF:EDIT:IDEL {p},{i}', False)
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def insert_profile_item(self, p: int, i: int, item: profile_item,
                            b1: float = None, b2: float = None):
        """Insert the selected item into the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).
        Items are zero-indexed, ranging from 0 to 255.

        Args:
            p (int): Selected profile
            i (int): Selected item index
            item (profile_item): Item instruction type
            b1 (float, optional): Optional parameter 1
            b2 (float, optional): Optional parameter 2
        """
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                match [item, b1, b2]:
                    case [profile_item.END
                          | profile_item.LOOP_END
                          | profile_item.STOP
                          | profile_item.HEATING_AND_COOLING
                          | profile_item.HEATING_ONLY
                          | profile_item.COOLING_ONLY, None, None]:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},{item.value}', False)
                    case [profile_item.HOLD, x,
                          None] if temperature.is_in_operation_range(self, x):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.RPP, x,
                          None] if temperature.is_in_power_range(self, x):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.WAIT, x,
                          None] if x >= 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.LOOP_BEGIN, x,
                          None] if x >= 0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{int(b1)}', False)
                    case [profile_item.RAMP,
                          x, y] if (
                              temperature.is_in_operation_range(self, x)
                              and temperature.is_in_ramp_rate_range(self, y)):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case [profile_item.PURGE,
                          x, y] if x >= 0.0 and y > 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case _:
                        raise ValueError('Invalid item/parameters')
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def add_profile_item(self, p: int, item: profile_item,
                         b1: float = None, b2: float = None):
        """Adds items to the end of the profile.

        Args:
            p (int): Selected profile
            item (profile_item): Item instruction type
            b1 (float, optional): Optional parameter 1
            b2 (float, optional): Optional parameter 2
        """
        self.insert_profile_item(
            p, self.get_profile_item_count(p), item, b1, b2)

    def get_profile_item(self, p: int, i: int):
        """Get the selected item from the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).
        Items are zero-indexed, ranging from 0 to 255.

        Args:
            p (int): Selected profile
            i (int): Selected item index

        Returns:
            (profile_item, float, float): Profile item tuple
        """
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                item_raw = self._controller._send_command(
                    f'PROF:EDIT:IRE {p},{i}').split(',')
                item = profile_item(int(item_raw[0]))
                b1 = float(item_raw[1]) if (item in [
                    profile_item.HOLD,
                    profile_item.RPP,
                    profile_item.WAIT,
                    profile_item.LOOP_BEGIN,
                    profile_item.RAMP,
                    profile_item.PURGE]) else None
                b2 = float(item_raw[2]) if (item in [
                    profile_item.PURGE,
                    profile_item.RAMP]) else None

                return item, b1, b2
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def set_profile_item(self, p: int, i: int, item: profile_item = None,
                         b1: float = None, b2: float = None):
        """Set the selected item in the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).
        Items are zero-indexed, ranging from 0 to 255.

        Args:
            p (int): Selected profile
            i (int): Selected item index
            item (profile_item): Item instruction type
        """
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                if item is None:
                    item = self.get_profile_item(p, i)[0]
                match [item, b1, b2]:
                    case [profile_item.END
                          | profile_item.LOOP_END
                          | profile_item.STOP
                          | profile_item.HEATING_AND_COOLING
                          | profile_item.HEATING_ONLY
                          | profile_item.COOLING_ONLY, None, None]:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},{item.value}', False)
                    case [profile_item.HOLD, x,
                          None] if temperature.is_in_operation_range(self, x):
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.RPP, x,
                          None] if temperature.is_in_power_range(self, x):
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.WAIT, x,
                          None] if x >= 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.LOOP_BEGIN, x,
                          None] if x >= 0:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{int(b1)}', False)
                    case [profile_item.RAMP,
                          x, y] if (
                              temperature.is_in_operation_range(self, x)
                              and temperature.is_in_ramp_rate_range(self, y)):
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case [profile_item.PURGE,
                          x, y] if x >= 0.0 and y > 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case _:
                        raise ValueError('Invalid item/parameters')
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def get_profile_item_count(self, p: int):
        """Get the number of items in the selected profile.

        Args:
            p (int): Selected profile

        Raises:
            ValueError: If profile is invalid

        Returns:
            int: Number of items
        """
        if self.is_valid_profile(p):
            return int(self._controller._send_command(
                f'PROF:EDIT:IC {int(p)}'))
        else:
            raise ValueError('Invalid profile')

    def get_profile_name(self, p: int):
        """Get the profile name of the selected profile.

        Args:
            p (int): Selected profile

        Raises:
            ValueError: If profile is invalid

        Returns:
            str: Profile name
        """
        if self.is_valid_profile(p):
            return self._controller._send_command(
                f'PROF:EDIT:GNAM {int(p)}').strip()
        else:
            raise ValueError('Invalid profile')

    def set_profile_name(self, p: int, name: str):
        """Set the profile name of the selected profile.

        Args:
            p (int): Selected profile
            name (str): Profile name

        Raises:
            ValueError: If name is too long (greater than 15 characters)
            ValueError: If profile is invalid
        """
        if self.is_valid_profile(p):
            if len(name) < 15:
                self._controller._send_command(
                    f'PROF:EDIT:SNAM {int(p)},"{str(name)}"', False)
            else:
                raise ValueError('Name is too long')
        else:
            raise ValueError('Invalid profile')

    def is_valid_profile(self, p: int):
        """Check if selected profile is valid.

        Args:
            p (int): Selected profile

        Returns:
            bool: True if in range, False otherwise
        """
        return p >= 0 and p < self.PROFILE_NUM

    def is_valid_item_index(self, i: int):
        """Check if selected item index is valid.

        Args:
            i (int): Selected item index

        Returns:
            bool: True if in range, False otherwise
        """
        return i >= 0 and i < self.ITEM_NUM
