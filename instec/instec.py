"""Instec library for performing simple SCPI commands via Python. Instead of
interfacing with the device manually via USB or Ethernet, the controller class
will setup the necessary serial ports or sockets for you. All commands
available in V3.21 of the SCPI Command Guide, such as HOLD or RAMP, have been
abstracted into Python functions for your convenience.
"""


from instec.controller import controller, mode
import instec.temperature as temperature
import instec.profile as profile


class instec(temperature, profile):
    def __init__(self, mode=mode.USB, baudrate=38400, port='COM3'):
        self._controller = controller(mode, baudrate, port)
        
    def connect(self):
        self._controller.connect()
        
    def is_connected(self):
        self._controller.is_connected()
        
    def disconnect(self):
        self._controller.disconnect()