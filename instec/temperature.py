"""Abstract class for controller temperature commands.
"""

from abc import ABC, abstractmethod
from instec.constants import (system_status, profile_status,
                              temperature_mode, unit)


class temperature(ABC):
    """All temperature related commands.
    """

    @abstractmethod
    def get_system_information(self) -> tuple[str, str, str, str]:
        """Information about the system:
        company (str): Company name
        model (str): Model number
        serial (str): Serial number
        firmware (str): firmware version

        Returns:
            (str, str, str, str): Tuple of system information.
        """
        pass

    @abstractmethod
    def get_runtime_information(self) -> tuple[int, float, float, float, float,
                                               float, float, system_status,
                                               profile_status, int, int, int]:
        """Return runtime information, such as temperatures, execution
        statuses, and error codes. Refer to the SCPI manual for a more
        detailed description on return values. Here is a short description
        of all returned values:
        sx (int):           Active slave number
        pv (float):         Process Variable (PV) – Current temperature of
                            the Stage/Plate/Chuck (°C)
        mv (float):         Monitor Value (MV) – Value used to measure
                            monitor temperature (°C)
        tsp (float):        Target Set Point (TSP) – Final target temperature
                            for Hold or Ramp command (°C)
        csp (float):        Current Set Point (CSP) – Current target
                            temperature (°C)
        rt (float):         Ramp Rate (RT) – Rate of PV change during Ramp
                            command (°C/minute)
        pp (float):         Percent Power (PP) – Percentage of total output
                            power being applied to Stage/Plate/Chuck (%)
        s_status (system_status):     Current system status code
        p_status (profile_status):    Current profile execution status code
        p (int):            Active profile number
        i (int):            Current index of profile during execution
        error_status (int): Error code status ID

        Returns:
            (int, float, float, float, float, float, float, system_status,
            profile_status, int, int, int): Tuple with information about the
            controller at runtime.
        """
        pass

    @abstractmethod
    def get_process_variables(self) -> tuple[float, ...]:
        """Return process variable values for connected slaves.

        Returns:
            (float tuple):  Process Variable (PV) – Current temperature of
                            all connected slaves
        """
        pass

    @abstractmethod
    def get_monitor_values(self) -> tuple[float, ...]:
        """Return monitor values for connected slaves.

        Returns:
            (float tuple):  Monitor Value (MV) – Monitor temperature of all
                            connected slaves
        """
        pass

    @abstractmethod
    def get_protection_sensors(self) -> tuple[float, ...]:
        """Return protection sensor values for connected slaves.

        Returns:
            (float tuple): Protection sensor value of all connected slaves.
        """
        pass

    @abstractmethod
    def hold_check(self, tsp: float) -> None:
        """Takes the desired setpoint (tsp) as a parameter, and will attempt
        to reach the TSP as fast as possible, and hold that value until
        directed otherwise. Passing a value outside of the controller's range
        will trigger Error Code 4 on the device.

        Args:
            tsp (float):    Target Set Point (TSP) – Final target temperature
                            for Hold or Ramp command (°C)

        Raises:
            ValueError: If tsp is out of range
        """
        pass

    @abstractmethod
    def hold(self, tsp: float) -> None:
        """Takes the desired setpoint (tsp) as a parameter, and will attempt
        to reach the TSP as fast as possible, and hold that value until
        directed otherwise.

        Args:
            tsp (float):    Target Set Point (TSP) – Final target temperature
                            for Hold or Ramp command (°C)
        """
        pass

    @abstractmethod
    def ramp_check(self, tsp: float, rt: float) -> None:
        """Takes the desired setpoint (tsp) and ramp rate (rt) as parameters,
        and will attempt to reach the current setpoint value according to the
        specified ramp rate until it reaches the setpoint. Once it reaches the
        target, it will maintain that value until directed otherwise. Passing a
        value outside of the controller's range will trigger Error Code 4 on
        the device.

        Args:
            tsp (float):    Target Set Point (TSP) – Final target temperature
                            for Hold or Ramp command (°C)
            rt (float):     Ramp Rate (RT) – Rate of PV change during Ramp
                            command (°C/minute)

        Raises:
            ValueError: If tsp is out of range
        """
        pass

    @abstractmethod
    def ramp(self, tsp: float, rt: float) -> None:
        """Takes the desired setpoint (tsp) and ramp rate (rt) as parameters,
        and will attempt to reach the current setpoint value according to the
        specified ramp rate until it reaches the setpoint. Once it reaches the
        target, it will maintain that value until directed otherwise.

        Args:
            tsp (float):    Target Set Point (TSP) – Final target temperature
                            for Hold or Ramp command (°C)
            rt (float):     Ramp Rate (RT) – Rate of PV change during Ramp
                            command (°C/minute)
        """
        pass

    @abstractmethod
    def rpp_check(self, pp: float) -> None:
        """Takes the desired power level (PP) as a parameter, and will
        attempt to reach the PP level as fast as possible, and hold that value
        until directed otherwise. Passing a value outside of the controller's
        range will raise an error.

        Args:
            pp (float, optional): Value between -1.0 and 1.0.

        Raises:
            ValueError: If pp is out of range.
        """
        pass

    @abstractmethod
    def rpp(self, pp: float) -> None:
        """Takes the desired power level (PP) as a parameter, and will
        attempt to reach the PP level as fast as possible, and hold that value
        until directed otherwise.

        Args:
            pp (float, optional): Value between -1.0 and 1.0.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stops all currently running commands.
        """
        pass

    @abstractmethod
    def get_cooling_heating_status(self) -> temperature_mode:
        """Return the temperature control mode of the controller.

        Returns:
            (temperature_mode): Enum that corresponds to the selected
                                temperature mode.
        """
        pass

    @abstractmethod
    def set_cooling_heating_status(self, status: temperature_mode) -> None:
        """Set the temperature control mode of the controller.

        Args:
            status (temperature_mode, optional): Enum that corresponds to the
                                                 selected temperature mode.

        Raises:
            ValueError: If temperature mode is invalid.
        """
        pass

    @abstractmethod
    def get_ramp_rate_range(self) -> tuple[float, float, float, float, float]:
        """Get the range of the ramp rate for the controller:
        max (float): Maximum rt value (°C/minute).
        min (float): Minimum rt value (°C/minute).
        limit_value (float): Limit value for alternate rt range (°C/minute).
        limit_max (float): Maximum rt value at limit (°C/minute).
        limit_min (float): Minimum rt value at limit (°C/minute).

        Returns:
            (float, float, float, float, float):    Tuple about the ramp rate
                                                    range of the controller.
        """
        pass

    @abstractmethod
    def get_stage_range(self) -> tuple[float, float]:
        """Get the stage temperature range.

        Returns:
            (float, float): Tuple of max and min stage temperatures.
        """
        pass

    @abstractmethod
    def get_operation_range(self) -> tuple[float, float]:
        """Get the operation temperature range.
        max (float): The maximum stage operation temperature.
        min (float): The minimum stage operation temperature.

        Returns:
            (float, float): Tuple of max and min operation temperatures.
        """
        pass

    @abstractmethod
    def set_operation_range(self, max: float, min: float) -> None:
        """Set the operation temperature range.

        Args:
            max (float): The maximum stage operation temperature.
            min (float): The minimum stage operation temperature.

        Raises:
            ValueError: If provided range is out of stage temperature range
            ValueError: If the max value is smaller than the min value
        """
        pass

    @abstractmethod
    def get_default_operation_range(self) -> tuple[float, float]:
        """Get the default operation temperature range.

        Returns:
            (float, float): Tuple of max and min default
                            operation temperatures.
        """
        pass

    @abstractmethod
    def get_system_status(self) -> system_status:
        """Get the current system status.

        Returns:
            system_status: The current system status.
        """
        pass

    @abstractmethod
    def get_serial_number(self) -> str:
        """Get the serial number.

        Returns:
            str: The serial number of the device.
        """
        pass

    @abstractmethod
    def get_set_point_temperature(self) -> float:
        """Get the Target Set Point (TSP) temperature.

        Returns:
            float: The set point temperature in °C.
        """
        pass

    @abstractmethod
    def get_ramp_rate(self) -> float:
        """Get the Ramp Rate (RT).

        Returns:
            float: The ramp rate in °C/minute.
        """
        pass

    @abstractmethod
    def get_power(self) -> float:
        """Get the current Power Percent (PP).

        Returns:
            float: The power percent.
        """
        pass

    @abstractmethod
    def get_powerboard_temperature(self) -> float:
        """Get the temperature of the powerboard RTD.

        Returns:
            float: The RTD temperature in °C.
        """
        pass

    @abstractmethod
    def get_error(self) -> int:
        """Get the current error (see SCPI manual for more details).

        Returns:
            int: The current error code.
        """
        pass

    @abstractmethod
    def get_operating_slave(self) -> int:
        """Get the current operating slave.
        Operating slaves are 1 indexed, up to a maximum of 4.

        Returns:
            int: The number of the current operating slave.
        """
        pass

    @abstractmethod
    def set_operating_slave(self, slave: int) -> None:
        """Set the current operating slave.
        Operating slaves are 1 indexed, up to a maximum of 4.

        Args:
            slave (int): The number of the operating slave.

        Raises:
            ValueError: If invalid number provided based on slave count.
        """
        pass

    @abstractmethod
    def get_slave_count(self) -> int:
        """Get the number of slaves connected to the current controller.

        Returns:
            int: The number of slaves connected.
        """
        pass

    @abstractmethod
    def purge(self, delay: float, hold: float) -> None:
        """Complete a gas purge on the device.

        Args:
            delay (float):  Amount of time to delay before performing the
                            purge in seconds.
            hold (float):   Amount of time to hold the gas purge in seconds.

        Raises:
            ValueError: If hold value is not greater than 0
            ValueError: If delay value is not greater than or equal to 0
        """
        pass

    @abstractmethod
    def get_pv_unit_type(self) -> unit:
        """Get the unit type of the Process Variable (PV).

        Returns:
            unit: Enum representing the unit type.
        """
        pass

    @abstractmethod
    def get_mv_unit_type(self) -> unit:
        """Get the unit type of the Monitor Value (MV).

        Returns:
            unit: Enum representing the unit type.
        """
        pass

    @abstractmethod
    def get_precision(self) -> tuple[int, int]:
        """Get the decimal precision of the Process Variable (PV)
        and Monitor Value (MV). Returns a tuple of both values:
        pv_precision (int): decimal precision of PV
        mv_precision (int): decimal precision of MV

        Returns:
            (int, int): Tuple of PV and MV precision
        """
        pass

    @abstractmethod
    def get_process_variable(self) -> float:
        """Get the process variable of the current operating slave.

        Returns:
            float: Process variable
        """
        pass

    @abstractmethod
    def get_monitor_value(self) -> float:
        """Get the monitor value of the current operating slave.

        Returns:
            float: Monitor value
        """
        pass

    @abstractmethod
    def get_protection_sensor(self) -> float:
        """Get the Protection sensor of the current operating slave.

        Returns:
            float: Protection sensor
        """
        pass

    @abstractmethod
    def get_power_range(self) -> tuple[float, float]:
        """ Get the power range.

        Returns:
            (float, float): max and min power range values.
        """
        pass

    @abstractmethod
    def is_in_power_range(self, pp: float) -> bool:
        """Check if pp value is in power range.

        Args:
            pp (float): Power percent

        Returns:
            bool: True if in range, False otherwise
        """
        pass

    @abstractmethod
    def is_in_ramp_rate_range(self, rt: float) -> bool:
        """Check if rt value is in ramp rate range.

        Args:
            rt (float): Ramp rate

        Returns:
            bool: True if in range, False otherwise
        """
        pass

    @abstractmethod
    def is_in_operation_range(self, temp: float) -> bool:
        """Check if temp value is in operation range.

        Args:
            temp (float): Temperature

        Returns:
            bool: True if in range, False otherwise
        """
        pass
