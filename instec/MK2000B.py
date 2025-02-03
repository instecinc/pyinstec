"""MK2000B implementation for SCPI command set.
"""

from ast import literal_eval
from instec.temperature import temperature
from instec.pid import pid
from instec.profile import profile
from instec.command import command
from instec.constants import (temperature_mode, system_status,
                              unit, profile_status, pid_table,
                              profile_item)


class MK2000B(command, temperature, pid, profile):
    PID_INDEX_NUM = 8
    PROFILE_NUM = 5
    ITEM_NUM = 255

    def get_system_information(self):
        data = self._controller._send_command('*IDN?').strip().split(',')
        company = data[0]
        model = data[1]
        serial = data[2]
        firmware = data[3]
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
        s_status = system_status(int(rtin[8]))
        profile = rtin[9].split(',')
        p_status = profile_status(int(profile[0]))
        p = int(profile[1])
        i = int(profile[2])
        error_status = int(rtin[10])

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
        ps_raw = self._controller._send_command('TEMP:PTEM?')
        ps = literal_eval(f'({ps_raw},)')
        return ps

    def hold_check(self, tsp: float):
        if self.is_in_operation_range(tsp):
            error = int(
                self._controller._send_command(
                    f'TEMP:HOLD {float(tsp)}; ERR?'))
            if error == 4:
                self.stop()
                raise ValueError('Set point value is out of range')
        else:
            self.stop()
            raise ValueError('Set point value is out of range')

    def hold(self, tsp: float):
        self._controller._send_command(
            f'TEMP:HOLD {float(tsp)}', False)

    def ramp_check(self, tsp: float, rt: float):
        if self.is_in_operation_range(tsp):
            if self.is_in_ramp_rate_range(rt):
                error = int(
                    self._controller._send_command(
                        f'TEMP:RAMP {float(tsp)},{float(rt)}; ERR?'))
            else:
                self.stop()
                raise ValueError('Ramp rate is out of range')
            if error == 4:
                self.stop()
                raise ValueError('Set point value is out of range')
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
        status = self._controller._send_command('TEMP:CHSW?')
        return temperature_mode(int(status))

    def set_cooling_heating_status(self, status: temperature_mode):
        if isinstance(status, temperature_mode):
            self._controller._send_command(f'TEMP:CHSW {status.value}', False)
        else:
            raise ValueError('Temperature mode is invalid')

    def get_ramp_rate_range(self):
        range_raw = self._controller._send_command('TEMP:RTR?')
        range = range_raw.split(',')
        max = float(range[0])
        min = float(range[1])
        limit_value = float(range[2])
        limit_max = float(range[3])
        limit_min = float(range[4])
        return max, min, limit_value, limit_max, limit_min

    def get_stage_range(self):
        max, min = self._controller._send_command('TEMP:SRAN?').split(',')
        return float(max), float(min)

    def get_operation_range(self):
        max, min = self._controller._send_command('TEMP:RANG?').split(',')
        return float(max), float(min)

    def set_operation_range(self, max: float, min: float):
        if min <= max:
            smax, smin = self.get_stage_range()
            if min >= smin and max <= smax:
                self._controller._send_command(
                    f'TEMP:RANG {float(max)},{float(min)}', False)
            else:
                raise ValueError('Operation temperature range is out of '
                                 'stage temperature range')
        else:
            raise ValueError('max is smaller than min')

    def get_default_operation_range(self):
        max, min = self._controller._send_command('TEMP:DRAN?').split(',')
        return float(max), float(min)

    def get_system_status(self):
        return system_status(int(self._controller._send_command('TEMP:STAT?')))

    def get_serial_number(self):
        return self._controller._send_command('TEMP:SNUM?').strip()

    def get_set_point_temperature(self):
        return float(self._controller._send_command('TEMP:SPO?'))

    def get_ramp_rate(self):
        return float(self._controller._send_command('TEMP:RAT?'))

    def get_power(self):
        return float(self._controller._send_command('TEMP:POW?'))

    def get_powerboard_temperature(self):
        return float(self._controller._send_command('TEMP:TP?'))

    def get_error(self):
        return int(self._controller._send_command('TEMP:ERR?'))

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
        return unit(int(self._controller._send_command('TEMP:TCUN?')))

    def get_mv_unit_type(self):
        return unit(int(self._controller._send_command('TEMP:TMUN?')))

    def get_precision(self):
        precision = self._controller._send_command('TEMP:PREC?').split(',')
        pv_precision = int(precision[0])
        mv_precision = int(precision[1])
        return pv_precision, mv_precision

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
        range = self.get_ramp_rate_range()
        return rt >= range[1] and rt <= range[0]

    def is_in_operation_range(self, temp: float):
        max, min = self.get_operation_range()
        if temp >= min and temp <= max:
            return True
        else:
            return False

    def get_current_pid(self):
        pid = self._controller._send_command('TEMP:PID?').split(',')
        p = float(pid[0])
        i = float(pid[1])
        d = float(pid[2])
        return p, i, d

    def get_pid(self, state: int, index: int):
        if isinstance(state, pid_table):
            if self.is_valid_pid_index(index):
                pid = self._controller._send_command(
                    f'TEMP:GPID {state.value},{int(index)}').split(',')
                state = pid_table(int(pid[0]))
                index = int(pid[1])
                temp = float(pid[2])
                p = float(pid[3])
                i = float(pid[4])
                d = float(pid[5])
                return state, index, temp, p, i, d
            else:
                raise ValueError('Index is out of range')
        else:
            raise ValueError('State is invalid')

    def set_pid(self, state: pid_table, index: int,
                temp: float, p: float, i: float, d: float):
        if isinstance(state, pid_table):
            if self.is_valid_pid_index(index):
                if self.is_in_operation_range(temp):
                    if p > 0 and i >= 0 and d >= 0:
                        self._controller._send_command(
                            f'TEMP:SPID {state.value},{int(index)},'
                            f'{temp},{p},{i},{d}',
                            False)
                    else:
                        raise ValueError('PID value(s) are invalid')
                else:
                    raise ValueError('Temperature value is out of range')
            else:
                raise ValueError('Index is out of range')
        else:
            raise ValueError('State is invalid')

    def is_valid_pid_index(self, index: int):
        return index >= 0 and index < self.PID_INDEX_NUM

    def get_profile_state(self):
        info = self._controller._send_command('PROF:RTST?').split(',')
        p_status = profile_status(int(info[0]))
        p = int(info[1])
        i = int(info[2])

        return p_status, p, i

    def start_profile(self, p: int):
        if self.is_valid_profile(p):
            self._controller._send_command(f'PROF:STAR {p}', False)
        else:
            raise ValueError('Invalid profile')

    def pause_profile(self):
        self._controller._send_command('PROF:PAUS', False)

    def resume_profile(self):
        self._controller._send_command('PROF:RES', False)

    def stop_profile(self):
        self._controller._send_command('PROF:STOP', False)

    def delete_profile(self, p: int):
        if self.is_valid_profile(p):
            self._controller._send_command(f'PROF:EDIT:PDEL {p}', False)
        else:
            raise ValueError('Invalid profile')

    def delete_profile_item(self, p: int, i: int):
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                self._controller._send_command(
                    f'PROF:EDIT:IDEL {p},{i}', False)
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def insert_profile_item(self, p: int, i: int, item: profile_item,
                            b1: float = None, b2: float = None):
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                match [item, b1, b2]:
                    case [profile_item.END
                          | profile_item.LOOP_END
                          | profile_item.STOP
                          | profile_item.HEATING_AND_COOLING
                          | profile_item.HEATING_ONLY
                          | profile_item.COOLING_ONLY, None, None]:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},{item.value}', False)
                    case [profile_item.HOLD, x,
                          None] if self.is_in_operation_range(x):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.RPP, x,
                          None] if self.is_in_power_range(x):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.WAIT, x,
                          None] if x >= 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.LOOP_BEGIN, x,
                          None] if x >= 0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{int(b1)}', False)
                    case [profile_item.RAMP,
                          x, y] if (
                              self.is_in_operation_range(x)
                              and self.is_in_ramp_rate_range(y)):
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case [profile_item.PURGE,
                          x, y] if x >= 0.0 and y > 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IINS {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case _:
                        raise ValueError('Invalid item/parameters')
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def add_profile_item(self, p: int, item: profile_item,
                         b1: float = None, b2: float = None):
        self.insert_profile_item(
            p, self.get_profile_item_count(p), item, b1, b2)

    def get_profile_item(self, p: int, i: int):
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                item_raw = self._controller._send_command(
                    f'PROF:EDIT:IRE {p},{i}').split(',')
                item = profile_item(int(item_raw[0]))
                b1 = float(item_raw[1]) if (item in [
                    profile_item.HOLD,
                    profile_item.RPP,
                    profile_item.WAIT,
                    profile_item.LOOP_BEGIN,
                    profile_item.RAMP,
                    profile_item.PURGE]) else None
                b2 = float(item_raw[2]) if (item in [
                    profile_item.PURGE,
                    profile_item.RAMP]) else None

                return item, b1, b2
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def set_profile_item(self, p: int, i: int, item: profile_item = None,
                         b1: float = None, b2: float = None):
        if self.is_valid_profile(p):
            if self.is_valid_item_index(i):
                if item is None:
                    item = self.get_profile_item(p, i)[0]
                match [item, b1, b2]:
                    case [profile_item.END
                          | profile_item.LOOP_END
                          | profile_item.STOP
                          | profile_item.HEATING_AND_COOLING
                          | profile_item.HEATING_ONLY
                          | profile_item.COOLING_ONLY, None, None]:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},{item.value}', False)
                    case [profile_item.HOLD, x,
                          None] if self.is_in_operation_range(x):
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.RPP, x,
                          None] if self.is_in_power_range(x):
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.WAIT, x,
                          None] if x >= 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)}', False)
                    case [profile_item.LOOP_BEGIN, x,
                          None] if x >= 0:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{int(b1)}', False)
                    case [profile_item.RAMP,
                          x, y] if (
                              self.is_in_operation_range(x)
                              and self.is_in_ramp_rate_range(y)):
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case [profile_item.PURGE,
                          x, y] if x >= 0.0 and y > 0.0:
                        self._controller._send_command(
                            f'PROF:EDIT:IED {p},{i},'
                            f'{item.value},{float(b1)},{float(b2)}', False)
                    case _:
                        raise ValueError('Invalid item/parameters')
            else:
                raise ValueError('Invalid item index')
        else:
            raise ValueError('Invalid profile')

    def get_profile_item_count(self, p: int):
        if self.is_valid_profile(p):
            return int(self._controller._send_command(
                f'PROF:EDIT:IC {int(p)}'))
        else:
            raise ValueError('Invalid profile')

    def get_profile_name(self, p: int):
        if self.is_valid_profile(p):
            return self._controller._send_command(
                f'PROF:EDIT:GNAM {int(p)}').strip()
        else:
            raise ValueError('Invalid profile')

    def set_profile_name(self, p: int, name: str):
        if self.is_valid_profile(p):
            if len(name) < 15:
                self._controller._send_command(
                    f'PROF:EDIT:SNAM {int(p)},"{str(name)}"', False)
            else:
                raise ValueError('Name is too long')
        else:
            raise ValueError('Invalid profile')

    def is_valid_profile(self, p: int):
        return p >= 0 and p < self.PROFILE_NUM

    def is_valid_item_index(self, i: int):
        return i >= 0 and i < self.ITEM_NUM
