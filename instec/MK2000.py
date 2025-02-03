"""Legacy support for the Instec Python library. Please use MK2000B if
possible, since this will be deprecated.
"""

from instec.MK2000B import MK2000B


class MK2000(MK2000B):
    pass
