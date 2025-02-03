from ast import literal_eval
from instec.temperature import temperature
from instec.command import command
from instec.constants import (temperature_mode, system_status,
                              unit, profile_status)


class MK2000VCP(command, temperature):
    PID_INDEX_NUM = 8
    PROFILE_NUM = 5
    ITEM_NUM = 255

    def get_system_information(self):
        data = self._controller._send_command('*IDN?').strip().split(',')
        company = data[0]
        model = data[1]
        # VCP returns master/slave here instead of serial number
        # serial = data[2]
        firmware = data[3]

        serial = self.get_serial_number()

        return company, model, serial, firmware

    def get_runtime_information(self):
        rtin_raw = self._controller._send_command('TEMP:RTIN?')
        rtin = (rtin_raw.split('MK')[1]).split(':')
        sx = int(rtin[1])
        pv = float(rtin[2])
        mv = float(rtin[3])
        tsp = float(rtin[4])
        csp = float(rtin[5])
        rt = float(rtin[6])
        pp = float(rtin[7])
        s_status = self._parse_vcp_system_status(int(rtin[8]))
        profile = rtin[9].split(',')
        p_status = profile_status(int(profile[0]))
        p = int(profile[1])
        i = int(profile[2])
        # Not supported by VCP controllers
        error_status = -1

        return (sx, pv, mv, tsp, csp, rt, pp, s_status, p_status,
                p, i, error_status)

    def get_process_variables(self):
        pv_raw = self._controller._send_command('TEMP:CTEM?')
        pv = literal_eval(f'({pv_raw},)')
        return pv

    def get_monitor_values(self):
        mv_raw = self._controller._send_command('TEMP:MTEM?')
        mv = literal_eval(f'({mv_raw},)')
        return mv

    def get_protection_sensors(self):
        # Not supported
        raise NotImplementedError

    def hold_check(self, tsp: float):
        if self.is_in_operation_range(tsp):
            self._controller._send_command(
                    f'TEMP:HOLD {float(tsp)}', False)
        else:
            self.stop()
            raise ValueError('Set point value is out of range')

    def hold(self, tsp: float):
        self._controller._send_command(
            f'TEMP:HOLD {float(tsp)}', False)

    def ramp_check(self, tsp: float, rt: float):
        if self.is_in_operation_range(tsp):
            self._controller._send_command(
                    f'TEMP:RAMP {float(tsp)},{float(rt)}', False)
        else:
            self.stop()
            raise ValueError('Set point value is out of range')

    def ramp(self, tsp: float, rt: float):
        self._controller._send_command(
            f'TEMP:RAMP {float(tsp)},{float(rt)}', False)

    def rpp_check(self, pp: float):
        if self.is_in_power_range(pp):
            self._controller._send_command(f'TEMP:RPP {float(pp)}', False)
        else:
            self.stop()
            raise ValueError('Power percentage is out of range')

    def rpp(self, pp: float):
        self._controller._send_command(f'TEMP:RPP {float(pp)}', False)

    def stop(self):
        self._controller._send_command('TEMP:STOP', False)

    def get_cooling_heating_status(self):
        status = self._controller._send_command('TEMP:COOL?')
        return temperature_mode(int(status))

    def set_cooling_heating_status(self, status: temperature_mode):
        if isinstance(status, temperature_mode):
            self._controller._send_command(f'TEMP:COOL {status.value}', False)
        else:
            raise ValueError('Temperature mode is invalid')

    def get_ramp_rate_range(self):
        # Not supported
        raise NotImplementedError

    def get_stage_range(self):
        # Not supported
        raise NotImplementedError

    def get_operation_range(self):
        max, min = self._controller._send_command('TEMP:RANG?').split(',')
        return float(max), float(min)

    def set_operation_range(self, max: float, min: float):
        if min <= max:
            self._controller._send_command(
                    f'TEMP:RANG {float(max)},{float(min)}', False)
        else:
            raise ValueError('max is smaller than min')

    def get_default_operation_range(self):
        # Not supported
        raise NotImplementedError

    def get_system_status(self):
        status = int(self._controller._send_command('TEMP:STAT?'))
        return self._parse_vcp_system_status(status)

    def _parse_vcp_system_status(self, status: int) -> system_status:
        match(status):
            case 5:
                return system_status.STOP
            case 21:
                return system_status.RPP
            case _:
                return system_status(status)

    def get_serial_number(self):
        return self._controller._send_command('TEMP:SNUM?').strip()

    def get_set_point_temperature(self):
        return float(self._controller._send_command('TEMP:SPO?'))

    def get_ramp_rate(self):
        return self.get_runtime_information()[5]

    def get_power(self):
        # Not supported
        return self.get_runtime_information()[6]

    def get_powerboard_temperature(self):
        # Not supported
        raise NotImplementedError

    def get_error(self):
        # Not supported
        raise NotImplementedError

    def get_operating_slave(self):
        return int(self._controller._send_command('TEMP:OPSL?'))

    def set_operating_slave(self, slave: int):
        if slave >= 1 and slave <= self.get_slave_count():
            self._controller._send_command(f'TEMP:OPSL {int(slave)}', False)
        else:
            raise ValueError('Invalid operating slave number')

    def get_slave_count(self):
        return int(self._controller._send_command('TEMP:SLAV?'))

    def purge(self, delay: float, hold: float):
        if delay >= 0:
            if hold > 0:
                self._controller._send_command(
                    f'TEMP:PURG {float(delay)},{float(hold)}', False)
            else:
                raise ValueError('Hold must be greater than 0')
        else:
            raise ValueError('Delay is less than 0')

    def get_pv_unit_type(self):
        # Not supported
        raise NotImplementedError

    def get_mv_unit_type(self):
        # Not supported
        raise NotImplementedError

    def get_precision(self):
        # Not supported
        raise NotImplementedError

    def get_process_variable(self):
        return self.get_process_variables()[self.get_operating_slave() - 1]

    def get_monitor_value(self):
        return self.get_monitor_values()[self.get_operating_slave() - 1]

    def get_protection_sensor(self):
        return self.get_protection_sensors()[self.get_operating_slave() - 1]

    def get_power_range(self):
        status = self.get_cooling_heating_status()
        min = 0.0 if status == temperature_mode.HEATING_ONLY else -1.0
        max = 0.0 if status == temperature_mode.COOLING_ONLY else 1.0
        return max, min

    def is_in_power_range(self, pp: float):
        max, min = self.get_power_range()
        return pp >= min and pp <= max

    def is_in_ramp_rate_range(self, rt: float):
        # Not supported
        raise NotImplementedError

    def is_in_operation_range(self, temp: float):
        max, min = self.get_operation_range()
        if temp >= min and temp <= max:
            return True
        else:
            return False
