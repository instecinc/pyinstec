"""Instec inherits all command sets, combining
them to work under one controller instance.
"""

from instec.temperature import temperature
from instec.profile import profile
from instec.pid import pid


class MK2000(temperature, profile, pid):
    """Obtain functions of implemented command set classes.
    """
    pass
