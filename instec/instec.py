"""The instec class inherits all command sets.
"""

from instec.temperature import temperature
from instec.profile import profile
from instec.pid import pid


class instec(temperature, profile, pid):
    pass