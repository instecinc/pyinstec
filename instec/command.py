"""Command class that all command sets inherit.
This class sets up the controller used for each command set.
"""

from instec.controller import controller, mode


class command:
    def get_ethernet_controllers():
        return controller.get_ethernet_controllers()

    def get_usb_controllers():
        return controller.get_usb_controllers()

    def __init__(self, conn_mode: mode = None,
                 baudrate: int = 38400, port: str = None,
                 serial_num: str = None, ip: str = None):
        """Initialize any relevant attributes necessary to connect to the
        controller, and define the connection mode.

        Args:
            conn_mode (mode, optional):    USB or Ethernet connection mode.
                                        Defaults to None.
            baudrate (int, optional):   Baud rate (for USB only).
                                        Defaults to 38400.
            port (str, optional):       Serial port (for USB only).
                                        Defaults to None.
        """
        self._controller = controller(conn_mode, baudrate,
                                      port, serial_num, ip)

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
