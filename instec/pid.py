"""Command set for PID commands.
"""

from abc import ABC, abstractmethod
from instec.constants import pid_table


class pid(ABC):
    """Abstract class for controller PID commands.
    """

    @abstractmethod
    def get_current_pid(self) -> tuple[float, float, float]:
        """Get the current PID value.
        p (float): The proportional value
        i (float): The integral value
        d (float): The derivative value

        Returns:
            (float, float, float): PID tuple
        """
        pass

    @abstractmethod
    def get_pid(self, state: int, index: int) -> tuple[int, int,
                                                       float, float, float]:
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
        pass

    @abstractmethod
    def set_pid(self, state: pid_table, index: int,
                temp: float, p: float, i: float, d: float) -> None:
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
        pass

    @abstractmethod
    def is_valid_pid_index(self, index: int) -> bool:
        """Check if selected PID index is valid.

        Args:
            index (int): Selected PID index

        Returns:
            bool: True if in range, False otherwise
        """
        pass
