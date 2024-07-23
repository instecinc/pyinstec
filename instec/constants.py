"""All defined enums used in each command set.
"""

from enum import Enum


class connection:
    TIMEOUT = 1
    ETHERNET_PORT = 'eth0'
    IP_ADDRESS = None


class mode(Enum):
    """Enums for connection mode.
    """
    USB = 0
    ETHERNET = 1


class system_status(Enum):
    """Enums for system status.
    """
    STOP = 0
    HOLD = 1
    RAMP = 2
    PAUSE = 3
    PROFILE = 4
    RPP = 5
    PURGE = 6


class temperature_mode(Enum):
    """Enums for temperature mode selection.
    """
    HEATING_ONLY = 0
    HEATING_AND_COOLING = 1
    COOLING_ONLY = 2


class unit(Enum):
    """Enums for controller unit usage.
    """
    CELCIUS = 1
    KELVIN = 2
    FAHRENHEIT = 3
    RELATIVE_HUMIDITY = 4
    PASCAL = 5
    BAR = 6
    POUND_PER_SQUARE_INCH = 7
    TORR = 8
    KILOPASCAL = 9
    VOLT = 10
    NEWTON = 11


class profile_status(Enum):
    """Enums for profile status.
    """
    STOP = 0
    RUN = 1
    PAUSE = 2


class profile_item(Enum):
    """Enums for profile item instruction type.
    """
    END = 0
    HOLD = 1
    RAMP = 2
    WAIT = 3
    LOOP_BEGIN = 4
    LOOP_END = 5
    PURGE = 6
    STOP = 7
    HEATING_AND_COOLING = 8
    HEATING_ONLY = 9
    RPP = 10
    COOLING_ONLY = 11


class pid_table(Enum):
    """Enums for PID table selection.
    """
    HEATING_HNC = 0     # Heating in Heating & Cooling (HNC) Mode
    COOLING_HNC = 1     # Cooling in Heating & Cooling (HNC) Mode
    HEATING_HO = 2      # Heating in Heating Only (HO) Mode
    COOLING_CO = 3      # Cooling in Cooling Only (CO) Mode
