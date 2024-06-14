"""Command class that all command sets inherit.
This class sets up the controller used for each command set.
"""

from instec.controller import controller, mode


class command:
    def __init__(self, conn_mode: mode = mode.USB,
                 baudrate: int = 38400, port: str = 'COM3'):
        self._controller = controller(conn_mode, baudrate, port)

    def connect(self):
        self._controller.connect()

    def is_connected(self):
        return self._controller.is_connected()

    def disconnect(self):
        self._controller.disconnect()
