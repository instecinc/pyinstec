# PyInstec - The Instec Python SCPI Command Library

PyInstec is an implementation of the SCPI commands used to interact with Instec devices such as the MK2000B.
All basic SCPI commands, such as HOLD or RAMP, have been abstracted into Python functions for ease of use.
Before using this library, it is highly recommended that you read through the SCPI command guide to gain an understanding of what all relevant functions do.

- Github Page: https://github.com/instecinc/pyinstec
- Download Page: https://test.pypi.org/project/instec/

## Documentation
Documentation for each function is provided with the python file instec.py.

## Installation
Currently, the library only supports Python versions 3.10 or later, but may change later on to support older versions. It has been tested on Windows 11 in the Visual Studio Code development environment.

The Instec library requires pyserial version 3.0 or later to work. pyserial can be installed by calling
```shell
pip install pyserial
```

After installing pyserial, the instec library can be installed.
Currently, the library is only available on TestPyPI. To install the library, run
```shell
pip install --index-url https://test.pypi.org/simple/ instec
```

## Usage
To add the library to your python file, add the import

```python
import instec
```

then you can use the functions associated with the library.

### Connection

To connect to the MK2000/MK2000B controller, first choose whether to connect over USB or Ethernet, and setup the connection to the device over the desired connection type.
Then, instantiate the controller.

For USB:
```python
controller = instec.MK2000(instec.mode.USB, baudrate, port)
```
By default the baud rate and port are 38400 and 'COM3', respectively.

For Ethernet:
```python
controller = instec.MK2000(instec.mode.ETHERNET)
```

Then, to connect to the controller, simply call
```python
controller.connect()
```


If a connection is unable to be established, a RuntimeError will be raised.

After finishing a program, it is recommended to close the connection with the controller:
```python
controller.disconnect()
```

### Functions

All functions in instec.py are instance methods, meaning they must be called with an instance of the controller. For example,
to run a hold command at 50°C using the instantiated controller from above, you can call
```python
controller.hold(50.0)
```

The following is a table of the 33 SCPI commands available for use with the MK2000B and their Python counterpart implemented in this library:

There are two main categories of commands included with the library: Temperature and Profile commands. Temperature commands are generally used
to query important runtime information from the controller and execute temperature control commands, while Profile commands are used to create
profiles, which can be run directly on the controller without external input.

#### Temperature Commands

There are a total of 33 SCPI temperature commands implemented as Python functions in this library.

| SCPI Command                  | Python Function               | Usage                                     |
| :---------------------------: |:----------------------------: | :---------------------------------------: |
| *IDN?                         | get_system_information()      | Get system info                           |
| TEMPerature:RTINformation?    | get_runtime_information()     | Get runtime info                          |
| TEMPerature:CTEMperature?     | get_process_variables()       | Get PV temperatures                       |
| TEMPerature:MTEMperature?     | get_monitor_values()          | Get MV temperatures                       |
| TEMPerature:PTEMperature?     | get_protection_sensors()      | Get protection sensor temperatures        |
| TEMPerature:HOLD tsp          | hold(tsp)                     | Hold at TSP temperature                   |
| TEMPerature:RAMP tsp,rt       | ramp(tsp, rt)                 | Ramp to TSP temperature                   |
| TEMPerature:RPP pp            | rpp(pp)                       | Run at PP power level                     |
| TEMPerature:STOP              | stop()                        | Stop all temperature control              |
| TEMPerature:PID?              | get_current_pid()             | Get current PID value                     |
| TEMPerature:GPID state,index  | get_pid(state, index)         | Get PID at specified table and index      |
| TEMPerature:SPID state,index,temp,p,i,d | set_pid(state, index, temp, p, i, d) | Set PID at specified table and index |
| TEMPerature:CHSWitch?         | get_cooling_heating_status()  | Get the Heating/Cooling mode of the controller |
| TEMPerature:CHSWitch status   | set_cooling_heating_status(status)| Set the Heating/Cooling mode of the controller |
| TEMPerature:SRANge?           | get_stage_range()             | Get the stage temperature range           |
| TEMPerature:RANGe?            | get_operation_range()         | Get the operation temperature range       |
| TEMPerature:RANGe max,min     | set_operation_range(max, min) | Set the operation temperature range       |
| TEMPerature:DRANge?           | get_default_operation_range() | Get the default operation temperature range |
| TEMPerature:STATus?           | get_system_status()           | Get the current system status             |
| TEMPerature:SNUMber?          | get_serial_number()           | Get the system serial number              |
| TEMPerature:SPOint?           | get_set_point_temperature()   | Get the set point (TSP) temperature       |
| TEMPerature:RATe?             | get_ramp_rate()               | Get the current ramp rate                 |
| TEMPerature:RTRange?          | get_ramp_rate_range()         | Get the range of the ramp rate            |
| TEMPerature:POWer?            | get_power()                   | Get the current power value               |
| TEMPerature:TP?               | get_powerboard_temperature()  | Get the current powerboard RTD temperature |
| TEMPerature:ERRor?            | get_error()                   | Get the current error                     |
| TEMPerature:OPSLave?          | get_operating_slave()         | Get the operating slave                   |
| TEMPerature:OPSLave slave     | set_operating_slave(slave)    | Set the operating slave                   |
| TEMPerature:SLAVes?           | get_slave_count()             | Get the number of connected slaves        |
| TEMPerature:PURGe delay,hold  | purge(delay, hold)            | Complete a gas purge for the specified duration |
| TEMPerature:TCUNit?           | get_pv_unit_type()            | Get unit type of PV                       |
| TEMPerature:TMUNit?           | get_mv_unit_type()            | Get unit type of MV                       |
| TEMPerature:PRECision?        | get_precision()               | Get the decimal precision of PV and MV    |

7 additional functions have been implemented as well:

| Python Function               | Usage                                                   |
|:----------------------------: | :-----------------------------------------------------: |
| get_process_variable()        | Get the process variable of the current operating slave |
| get_monitor_value()           | Get the monitor value of the current operating slave    |
| get_protection_sensor()       | Get the protection sensor value of the current operating slave |
| get_power_range()             | Get the power range                                     |
| is_in_power_range(pp)         | Check if pp value is in power range                     |
| is_in_ramp_rate_range(pp)     | Check if rt value is in ramp rate range                 |
| is_in_operation_range(temp)   | Check if temp value is in operation range               |

More information on the Python temperature commands can be found in the temperature.py and pid.py files.

#### Profile Commands

There are a total of 13 SCPI profile commands implemented as Python functions in this library.

| SCPI Command                  | Python Function               | Usage                                     |
| :---------------------------: |:----------------------------: | :---------------------------------------: |
| PROFile:RTSTate?              | get_profile_state()           | Get the current profile state             |
| PROFile:STARt p               | start_profile(p)              | Start the selected profile.               |
| PROFile:PAUSe                 | pause_profile()               | Pauses the currently running profile      |
| PROFile:RESume                | resume_profile()              | Resumes the current profile               |
| PROFile:STOP                  | stop_profile()                | Stops the current profile                 |
| PROFile:EDIT:PDELete p        | delete_profile(p)             | Delete the selected profile               |
| PROFile:EDIT:IDELete p,i      | delete_profile_item(p, i)     | Delete the selected profile item          |
| PROFile:EDIT:IINSert p,i,c,b1,b2 | insert_profile_item(p, i, c, b1, b2) | Insert the selected item into the selected profile |
| PROFile:EDIT:IEDit p,i,c,b1,b2 | set_profile_item(p, i, c, b1, b2) | Set the selected item in the selected profile |
| PROFile:EDIT:IREad p,i        | get_profile_item(p, i)        | Get the selected item from the selected profile |
| PROFile:EDIT:ICount p         | get_profile_item_count(p)     | Get the number of items in the selected profile |
| PROFile:EDIT:GNAMe p          | get_profile_name(p)           | Get the profile name of the selected profile |
|PROFile:EDIT:SNAMe p,"name"    | set_profile_name(p, name)     | Set the profile name of the selected profile |

3 additional functions have been implemented as well:

| Python Function               | Usage                                                   |
|:----------------------------: | :-----------------------------------------------------: |
| add_profile_item(p, i, c, b1, b2) | Add item to the end of the profile                  |
| is_valid_profile(p)          | Check if selected profile is valid                       |
| is_valid_item_index(i)       | Check if selected item index is valid                    |

More information on the Python profile commands can be found in profile.py.

### Enums

Unlike the original SCPI implementation, some functions will require enums instead of integers. For example, to set the
Cooling/Heating mode of the controller to Heating Only using SCPI commands, you would call
```shell
TEMPerature:CHSWitch 0
```

In Python, the same command would be
```python
controller.set_cooling_heating_status(instec.temperature_mode.HEATING_ONLY)
```

The hope is by using enums, it is more obvious what each value accomplishes and parameters are less likely to be incorrectly set.

All enums can be seen in the instec.py file and correspond with their respective integer values in the SCPI command guide.
