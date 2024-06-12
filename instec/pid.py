from instec.command import command
from enum import Enum


class PID_table(Enum):
    """Enums for PID table selection.
    """
    HEATING_HNC = 0     # Heating in Heating & Cooling (HNC) Mode
    COOLING_HNC = 1     # Cooling in Heating & Cooling (HNC) Mode
    HEATING_HO = 2      # Heating in Heating Only (HO) Mode
    COOLING_CO = 3      # Cooling in Cooling Only (CO) Mode


class pid(command):
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

    def get_pid(self, state, index):
        """Get the PID value from PID table. Returns:
        state (PID_table):  The selected PID table
        index (int):        The selected table index
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
        if isinstance(state, PID_table):
            if index >= 0 and index < 8:
                pid = self._controller._send_command(
                    f'TEMP:GPID {state.value},{int(index)}').split(',')
                state = PID_table(int(pid[0]))
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

    def set_pid(self, state, index, temp, p, i, d):
        """Set the PID value in the specified PID table

        Args:
            state (PID_table):  The selected PID table
            index (int):        The selected table index
            p (float):          The proportional value
            i (float):          The integral value
            d (float):          The derivative value

        Raises:
            ValueError: If PID values are invalid
            ValueError: If temperature value is out of range
            ValueError: If index is out of range
            ValueError: If state is invalid
        """
        if isinstance(state, PID_table):
            if index >= 0 and index < 8:
                max, min = self.get_operation_range()
                if temp >= min and temp <= max:
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
