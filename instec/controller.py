"""Class that contains all of the functions setting up the connection
with the MK2000/MK2000B controller itself.
"""

import serial
import socket
import sys
from instec.constants import mode


class controller:
    """All basic communication functions to interface with the MK2000B.
    """

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

        Raises:
            ValueError: If invalid connection mode is given.
        """
        self._mode = conn_mode
        if self._mode == mode.USB:
            self._usb = serial.Serial()
            self._usb.baudrate = baudrate
            self._usb.port = port
        elif self._mode == mode.ETHERNET:
            self._controller_address = None
        else:
            raise ValueError('Invalid connection mode')

    def connect(self):

        """Connect to controller via selected connection mode.

        Raises:
            RuntimeError:   If unable to connect via COM port.
            RuntimeError:   If no UDP response is received.
            RuntimeError:   If TCP connection cannot be established.
            ValueError:     If invalid connection mode is given.
        """
        if self._mode == mode.USB:
            try:
                self._usb.open()
            except serial.SerialException as error:
                raise RuntimeError('Unable to connect via COM port') from error
        elif self._mode == mode.ETHERNET:
            # See MK2000 Ethernet Communication Guide for more information
            # Obtain controller IP from UDP message
            udp_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_receiver.bind(
                (socket.gethostbyname(socket.gethostname()),
                 50291))
            udp_receiver.settimeout(10)

            udp_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sender.sendto(
                bytes.fromhex('73C4000001'),
                ('255.255.255.255', 50290))

            try:
                self._controller_address = udp_receiver.recvfrom(1024)[1][0]
            except Exception as error:
                raise RuntimeError('Did not receive UDP response') from error

            udp_receiver.close()
            udp_sender.close()

            # Establish TCP connection with controller
            self._tcp_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM)
            self._tcp_socket.settimeout(10)

            try:
                self._tcp_socket.connect((self._controller_address, 50292))
            except OSError as error:
                if error.winerror == 10054:
                    self._tcp_socket.connect((self._controller_address, 50292))
            except Exception as error:
                raise RuntimeError('Unable to establish '
                                   'TCP connection') from error
        else:
            raise ValueError('Invalid connection mode')

    def disconnect(self):
        """Disconnect from the controller.

        Raises:
            ValueError: If invalid connection mode is given.
        """
        if self._mode == mode.USB:
            self._usb.close()
        elif self._mode == mode.ETHERNET:
            self._tcp_socket.close()
        else:
            raise ValueError('Invalid connection mode')

    def is_connected(self):
        """Check connection to controller.

        Raises:
            RuntimeError: If undesired exception occured.
            ValueError: If invalid connection mode is given.

        Returns:
            bool: True if connected, False otherwise.
        """
        if self._mode == mode.USB:
            return self._usb.is_open
        elif self._mode == mode.ETHERNET:
            try:
                timeout = self._tcp_socket.gettimeout()
                self._tcp_socket.settimeout(0)
                if sys.platform == "win32":
                    data = self._tcp_socket.recv(16, socket.MSG_PEEK)
                else:
                    data = self._tcp_socket.recv(16,
                                                 socket.MSG_DONTWAIT
                                                 | socket.MSG_PEEK)
                if len(data) == 0:
                    return False
            except BlockingIOError:
                return True
            except ConnectionResetError:
                return False
            except OSError as error:
                if sys.platform == "win32" and error.winerror == 10038:
                    return False
            except ValueError:
                return False
            except Exception as error:
                raise RuntimeError('Unknown exception occured') from error
            finally:
                try:
                    self._tcp_socket.settimeout(timeout)
                except OSError as error:
                    if sys.platform == "win32" and error.winerror == 10038:
                        pass
        else:
            raise ValueError('Invalid connection mode')

    def _send_command(self, command, returns=True):
        """Internal function to process and send SCPI commands via the
        desired communication method.

        Args:
            command (str):              The command to run in SCPI format.
            returns (bool, optional):   Whether the command should return.
                                        Defaults to True.

        Raises:
            RuntimeError: If the TCP socket is unable to receive anything.
            ValueError: If invalid connection mode is given.

        Returns:
            str: None if returns is False, otherwise the value from recv.
        """
        if self._mode == mode.USB:
            self._usb.write(str.encode(f'{command}\n'))
            if returns:
                buffer = self._usb.readline().decode()
                # Buffer must check if the returned string ends with \r\n,
                # otherwise it is possible the entire result was not sent
                # and readline should be called until the entire result is
                # received.
                while not buffer.endswith('\r\n'):
                    buffer += self._usb.readline().decode()
                return buffer
            else:
                return None
        elif self._mode == mode.ETHERNET:
            self._tcp_socket.send(str.encode(f'{command}\n'))
            if returns:
                try:
                    buffer = self._tcp_socket.recv(1024).decode()
                    # Buffer must check if the returned string ends with \r\n,
                    # otherwise it is possible the entire result was not sent
                    # and recv should be called until the entire result is
                    # received.
                    while not buffer.endswith('\r\n'):
                        buffer += self._tcp_socket.recv(1024).decode()
                    return buffer
                except Exception as error:
                    raise RuntimeError('Unable to receive response') from error
            else:
                return None
        else:
            raise ValueError('Invalid connection mode')
