from instec.command import command
from enum import Enum


class profile_status(Enum):
    """Enums for profile status.
    """
    STOP = 0
    RUN = 1
    PAUSE = 2

class profile(command):
    def get_profile_state(self):
        self._controller._send_command()
        pass
    
    