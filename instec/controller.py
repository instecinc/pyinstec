"""Class that contains all of the functions setting up the connection
with the MK2000/MK2000B controller itself.
"""

import serial
from serial.tools import list_ports
import socket
import sys
if sys.platform.startswith('linux'):
    import fcntl
    import struct
from instec.constants import mode, connection


class controller:
    """All basic communication functions to interface with the MK2000/MK2000B.
    """
    ethernet = []
    usb = []

    def _get_eth_addr():
        if isinstance(connection.IP_ADDRESS, str):
            return connection.IP_ADDRESS
        if sys.platform.startswith('win32'):
            return socket.gethostbyname(socket.gethostname())
        if sys.platform.startswith('linux'):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    return socket.inet_ntoa(
                        fcntl.ioctl(
                            s.fileno(),
                            0x8915,
                            struct.pack('256s',
                                        connection.ETHERNET_PORT.encode()
                                        ))[20:24])
            except Exception as error:
                raise RuntimeError('Issue finding ethernet port') from error
        else:
            raise RuntimeError('Unsupported OS')

    def get_ethernet_controllers():
        """Get all controllers connected via Ethernet.

        Returns:
            List: List of tuples in the form (serial_num, ip)
        """
        with (
            socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver,
                socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender):

            receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            receiver.bind((controller._get_eth_addr(), 50291))
            receiver.settimeout(connection.TIMEOUT)

            sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sender.sendto(
                bytes.fromhex('73C4000001'),
                ('255.255.255.255', 50290))

            controller.ethernet = []
            while True:
                try:
                    buffer, addr = receiver.recvfrom(1024)
                    buffer = buffer.decode()
                    data = buffer.strip().split(':')
                    model = data[0]
                    serial_num = data[1]
                    if model.startswith('IoT_MK#MK2000'):
                        controller.ethernet.append((serial_num, addr[0]))
                except socket.error:
                    break
                except Exception as error:
                    raise RuntimeError(
                        'Did not receive UDP response') from error

            return controller.ethernet

    def get_usb_controllers():
        """Get all controllers connected via USB.

        Returns:
            List: List of tuples in the form (serial_num, port)
        """
        ports = list_ports.comports()
        controller.usb = []
        for port in ports:
            conn = serial.Serial(port.device)
            conn.timeout = connection.TIMEOUT
            try:
                conn.open()

                conn.write(str.encode('TEMP:SNUM?'))

                buffer = conn.readline().decode()
                while not buffer.endswith('\r\n'):
                    buffer += conn.readline().decode()

                data = buffer.strip().split(',')
                company = data[0]
                model = data[1]
                serial_num = data[2]

                if company == 'Instec' and model.startswith('MK2000'):
                    controller.usb.append((serial_num, port.device))

            except Exception:
                continue

        return controller.usb

    def _get_controller_by_serial_number(self, serial_num: str):
        """Find the controller connection info by serial number.

        Args:
            serial_num (str): Serial number of the controller.

        Raises:
            ValueError: If a controller with the serial number is not found.

        Returns:
            List: List of tuples in the form (serial_num, param). where param
                  is either the port (USB) or IP address (Ethernet)
        """

        if self._mode in [mode.USB, None]:
            try:
                for c in controller.usb:
                    if c[0] == serial_num:
                        self._mode = mode.USB
                        return c[1]
                for c in controller.get_usb_controllers():
                    if c[0] == serial_num:
                        self._mode = mode.USB
                        return c[1]
            except TypeError:
                pass
        if self._mode in [mode.ETHERNET, None]:
            try:
                for c in controller.ethernet:
                    if c[0] == serial_num:
                        self._mode = mode.ETHERNET
                        return c[1]
                for c in controller.get_ethernet_controllers():
                    if c[0] == serial_num:
                        self._mode = mode.ETHERNET
                        return c[1]
            except TypeError:
                pass
        raise ValueError(f'Controller with serial number'
                         f'{serial_num} not connected.')

    def __init__(self, conn_mode: mode = None,
                 baudrate: int = 38400, port: str = None,
                 serial_num: str = None, ip: str = None):
        """Initialize any relevant attributes necessary to connect to the
        controller, and define the connection mode.

        Args:
            conn_mode (mode, optional):    USB or Ethernet connection mode.
                                        Defaults to None.
            baudrate (int, optional):   Baud rate (USB mode only).
                                        Defaults to 38400.
            port (str, optional):       Serial port (USB mode only).
                                        Defaults to None.
            serial_num (str, optional): Serial number of controller.
                                        Defaults to None.
            ip (str, optional):         IP address of controller
                                        (Ethernet mode only).
                                        Defaults to None.

        Raises:
            ValueError: If invalid connection mode is given.
        """
        self._mode = conn_mode
        if isinstance(serial_num, str):
            param = self._get_controller_by_serial_number(serial_num)
            if self._mode == mode.USB:
                port = param
            elif self._mode == mode.ETHERNET:
                ip = param

        if self._mode == mode.USB:
            self._usb = serial.Serial()
            if isinstance(baudrate, int):
                self._usb.baudrate = baudrate
            else:
                raise ValueError('Invalid baud rate')
            if isinstance(port, str):
                self._usb.port = port
        elif self._mode == mode.ETHERNET:
            if isinstance(ip, str):
                self._controller_address = ip
            else:
                raise ValueError('Invalid IP address')
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
            # Establish TCP connection with controller
            self._tcp_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM)
            # Change connection.TIMEOUT to adjust timeout
            self._tcp_socket.settimeout(connection.TIMEOUT)
            try:
                self._tcp_socket.connect((self._controller_address, 50292))
            except OSError as error:
                raise RuntimeError('Issues connecting to device') from error
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
                if sys.platform.startswith('win32'):
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
            except OSError:
                return False
            except ValueError:
                return False
            except Exception as error:
                raise RuntimeError('Unknown exception occured') from error
            finally:
                try:
                    self._tcp_socket.settimeout(timeout)
                except OSError:
                    pass
                except AttributeError:
                    return False
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
