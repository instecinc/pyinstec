"""Command set for profile commands.
"""

from abc import ABC, abstractmethod
from instec.constants import profile_status, profile_item


class profile(ABC):
    """All profile related commands.
    """

    @abstractmethod
    def get_profile_state(self) -> tuple[profile_status, int, int]:
        """Get the current profile state.
        p_status (profile_status):    Current profile execution status code
        p (int):            Active profile number
        i (int):            Current index of profile during execution

        Returns:
            (profile_status, int, int): Profile tuple
        """
        pass

    @abstractmethod
    def start_profile(self, p: int) -> None:
        """Start the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).

        Args:
            p (int): Selected profile
        """
        pass

    @abstractmethod
    def pause_profile(self) -> None:
        """Pauses the currently running profile, if applicable.
        This will allow the currently running instruction to
        finish, stopping before the next command.
        """
        pass

    @abstractmethod
    def resume_profile(self) -> None:
        """Resumes the currently running profile, if applicable.
        """
        pass

    @abstractmethod
    def stop_profile(self) -> None:
        """Stops the currently running/paused profile, if applicable.
        """
        pass

    @abstractmethod
    def delete_profile(self, p: int) -> None:
        """Delete the selected profile.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).

        Args:
            p (int): Selected profile
        """
        pass

    @abstractmethod
    def delete_profile_item(self, p: int, i: int) -> None:
        """Delete the selected profile item.
        Profiles are zero-indexed, ranging from 0 to 4, inclusive, but
        the default names are one-indexed (i.e. 0 corresponds with
        1 Profile, 1 corresponds with 2 Profile, etc.).
        Items are zero-indexed, ranging from 0 to 255.

        Args:
            p (int): Selected profile
            i (int): Selected item index
        """
        pass

    @abstractmethod
    def insert_profile_item(self, p: int, i: int, item: profile_item,
                            b1: float = None, b2: float = None) -> None:
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
        pass

    @abstractmethod
    def add_profile_item(self, p: int, item: profile_item,
                         b1: float = None, b2: float = None) -> None:
        """Adds items to the end of the profile.

        Args:
            p (int): Selected profile
            item (profile_item): Item instruction type
            b1 (float, optional): Optional parameter 1
            b2 (float, optional): Optional parameter 2
        """
        pass

    @abstractmethod
    def get_profile_item(self, p: int, i: int) -> None:
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
        pass

    @abstractmethod
    def set_profile_item(self, p: int, i: int, item: profile_item = None,
                         b1: float = None, b2: float = None) -> None:
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
        pass

    @abstractmethod
    def get_profile_item_count(self, p: int) -> int:
        """Get the number of items in the selected profile.

        Args:
            p (int): Selected profile

        Raises:
            ValueError: If profile is invalid

        Returns:
            int: Number of items
        """
        pass

    @abstractmethod
    def get_profile_name(self, p: int) -> str:
        """Get the profile name of the selected profile.

        Args:
            p (int): Selected profile

        Raises:
            ValueError: If profile is invalid

        Returns:
            str: Profile name
        """
        pass

    @abstractmethod
    def set_profile_name(self, p: int, name: str) -> None:
        """Set the profile name of the selected profile.

        Args:
            p (int): Selected profile
            name (str): Profile name

        Raises:
            ValueError: If name is too long (greater than 15 characters)
            ValueError: If profile is invalid
        """
        pass

    @abstractmethod
    def is_valid_profile(self, p: int) -> bool:
        """Check if selected profile is valid.

        Args:
            p (int): Selected profile

        Returns:
            bool: True if in range, False otherwise
        """
        pass

    @abstractmethod
    def is_valid_item_index(self, i: int) -> bool:
        """Check if selected item index is valid.

        Args:
            i (int): Selected item index

        Returns:
            bool: True if in range, False otherwise
        """
        pass
