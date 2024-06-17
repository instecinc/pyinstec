"""Command set for PID commands.
"""


from instec.command import command
from instec.constants import pid_table
from instec.temperature import temperature


class pid(command):
    """All PID related commands.
    """

    PID_INDEX_NUM = 8

    def get_current_pid(self):
        """Get the current PID value.
        p (float): The proportional value
        i (float): The integral value
        d (float): The derivative value

        Returns:
            (float, float, float): PID tuple
        """
        pid = self._controller._send_command('TEMP:PID?').split(',')
        p = float(pid[0])
        i = float(pid[1])
        d = float(pid[2])
        return p, i, d

    def get_pid(self, state: int, index: int):
        """Get the PID value from PID table. Returns:
        state (PID_table):  The selected PID table
        index (int):        The selected table index
        temp (float):       The temperature point
        p (float):          The proportional value
        i (float):          The integral value
        d (float):          The derivative value

        Args:
            state (PID_table): The PID table state (0-3)
            index (int): The table index (0-7)

        Raises:
            ValueError: If index is out of range
            ValueError: If state is invalid

        Returns:
            (int, int, float, float, float): PID tuple
        """
        if isinstance(state, pid_table):
            if self.is_valid_pid_index(index):
                pid = self._controller._send_command(
                    f'TEMP:GPID {state.value},{int(index)}').split(',')
                state = pid_table(int(pid[0]))
                index = int(pid[1])
                temp = float(pid[2])
                p = float(pid[3])
                i = float(pid[4])
                d = float(pid[5])
                return state, index, temp, p, i, d
            else:
                raise ValueError('Index is out of range')
        else:
            raise ValueError('State is invalid')

    def set_pid(self, state: pid_table, index: int,
                temp: float, p: float, i: float, d: float):
        """Set the PID value in the specified PID table

        Args:
            state (PID_table):  The selected PID table
            index (int):        The selected table index
            temp (float):       The temperature point
            p (float):          The proportional value
            i (float):          The integral value
            d (float):          The derivative value

        Raises:
            ValueError: If PID values are invalid
            ValueError: If temperature value is out of range
            ValueError: If index is out of range
            ValueError: If state is invalid
        """
        if isinstance(state, pid_table):
            if self.is_valid_pid_index(index):
                if temperature.is_in_operation_range(self, temp):
                    if p > 0 and i >= 0 and d >= 0:
                        self._controller._send_command(
                            f'TEMP:SPID {state.value},{int(index)},'
                            f'{temp},{p},{i},{d}',
                            False)
                    else:
                        raise ValueError('PID value(s) are invalid')
                else:
                    raise ValueError('Temperature value is out of range')
            else:
                raise ValueError('Index is out of range')
        else:
            raise ValueError('State is invalid')

    def is_valid_pid_index(self, index: int):
        """Check if selected PID index is valid.

        Args:
            index (int): Selected PID index

        Returns:
            bool: True if in range, False otherwise
        """
        return index >= 0 and index < self.PID_INDEX_NUM
