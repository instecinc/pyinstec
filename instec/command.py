"""Command class that all command sets inherit.
This class sets up the controller used for each command set.
"""

from instec.controller import controller, mode


class command:
    def __init__(self, conn_mode: mode = mode.USB,
                 baudrate: int = 38400, port: str = 'COM3'):
        """Initialize any relevant attributes necessary to connect to the
        controller, and define the connection mode.

        Args:
            conn_mode (mode, optional):    USB or Ethernet connection mode.
                                        Defaults to mode.USB.
            baudrate (int, optional):   Baud rate (for USB only).
                                        Defaults to 38400.
            port (str, optional):       Serial port (for USB only).
                                        Defaults to 'COM3'.
        """
        self._controller = controller(conn_mode, baudrate, port)

    def connect(self):
        """Connect to controller via selected connection mode.
        """
        self._controller.connect()

    def is_connected(self):
        """Check connection to controller.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self._controller.is_connected()

    def disconnect(self):
        """Disconnect from the controller.
        """
        self._controller.disconnect()
