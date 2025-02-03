# PyInstec - The Instec Python SCPI Command Library

PyInstec is an implementation of the SCPI commands used to interact with Instec devices such as the MK2000B.
All basic SCPI commands, such as HOLD or RAMP, have been abstracted into Python functions for ease of use.
Before using this library, it is highly recommended that you read through the SCPI command guide to gain an understanding of what all relevant functions do.

- Github Page: https://github.com/instecinc/pyinstec
- Download Page: https://pypi.org/project/instec/

## Temperature Controller Compatability
In it's current form, the Instec Python library is compatible with mK2000B temperature controllers - these controllers can easily be identified by the large 7" touchpad on the front panel - with **limited** support for mK2000VCP controllers. See the "Compatibility" section for more information.

## Installation
Currently, the library only supports Python versions 3.10 or later, but may change later on to support older versions. It has been tested on Windows 11 in the Visual Studio Code development environment.

The Instec library requires pyserial version 3.0 or later to work. pyserial can be installed by calling
```shell
pip install pyserial
```

After installing pyserial, the instec library can be installed.
```shell
pip install instec
```

To download the example and test codes in this repository, clone the repository. More info can be found in [this guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

## Usage
To add the library to your python file, add the import

```python
import instec
```

then you can use the functions associated with the library.

### Connection

To connect to the MK2000B/MK2000VCP controller, first choose whether to connect over USB or Ethernet, and setup the connection to the device over the desired connection type.

If you are unsure of what port or IP address your current controller has, you can call the commands `get_ethernet_controllers()` to retrieve all controllers connected via Ethernet and `get_usb_controllers()` to retrieve all controllers connected via USB. These functions will return a list of tuples of the serial number and IP address, and the serial number and port, respectively.

The controller can be instantiated in 3 different ways (Note: replace instec.MK2000B with instec.MK2000VCP if using an MK2000VCP controller):

If the connection mode is USB and the port is known:
```python
controller = instec.MK2000B(instec.mode.USB, baudrate, port)
```
Where `baudrate` and `port` are the baud rate and port of the device, respectively.
By default the baud rate is 38400.

If the connection mode is Ethernet and the IP address is known:
```python
controller = instec.MK2000B(instec.mode.ETHERNET, ip)
```
Where `ip` is the IP address of the controller.

If the connection mode is unknown and the serial number is known:
```python
controller = instec.MK2000B(serial_num)
```
Where serial_num is the serial number of the device.

To connect to the controller, call
```python
controller.connect()
```


If a connection is unable to be established, a RuntimeError will be raised.

After finishing a program, it is recommended to close the connection with the controller:
```python
controller.disconnect()
```

To check if a controller is connected, call
```python
controller.is_connected()
```

For the majority of users running the library on Linux, the designated Ethernet port is 'eth0'. In cases where a different Ethernet port is utilized to connect with the controller, modify the ETHERNET_PORT constant to the desired port.
For example, to switch the Ethernet port to 'eth1':
```python
instec.connection.ETHERNET_PORT = 'eth1'
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

| Python Function                       | Usage                                                 | MK2000B SCPI Command                      | MK2000VCP SCPI Command                    |
|:----------------------------:         | :---------------------------------------:             | :---------------------------:             | :---------------------------:             |
| get_system_information()              | Get system info                                       | *IDN?                                     | *IDN?                                     |
| get_runtime_information()             | Get runtime info                                      | TEMPerature:RTINformation?                | TEMPerature:RTINformation?                |
| get_process_variables()               | Get PV temperatures                                   | TEMPerature:CTEMperature?                 | TEMPerature:CTEMperature?                 |
| get_monitor_values()                  | Get MV temperatures                                   | TEMPerature:MTEMperature?                 | TEMPerature:MTEMperature?                 |
| get_protection_sensors()              | Get protection sensor temperatures                    | TEMPerature:PTEMperature?                 | N/A                                       |
| hold(tsp)                             | Hold at TSP temperature                               | TEMPerature:HOLD tsp                      | TEMPerature:HOLD tsp                      |
| ramp(tsp, rt)                         | Ramp to TSP temperature                               | TEMPerature:RAMP tsp,rt                   | TEMPerature:RAMP tsp,rt                   |
| rpp(pp)                               | Run at PP power level                                 | TEMPerature:RPP pp                        | TEMPerature:RPP pp                        |
| stop()                                | Stop all temperature control                          | TEMPerature:STOP                          | TEMPerature:STOP                          |
| get_cooling_heating_status()          | Get the Heating/Cooling mode of the controller        | TEMPerature:CHSWitch?                     | TEMPerature:COOLing?                      |
| set_cooling_heating_status(status)    | Set the Heating/Cooling mode of the controller        | TEMPerature:CHSWitch status               | TEMPerature:COOLing status                |
| get_stage_range()                     | Get the stage temperature range                       | TEMPerature:SRANge?                       | N/A                                       |
| get_operation_range()                 | Get the operation temperature range                   | TEMPerature:RANGe?                        | TEMPerature:RANGe?                        |
| set_operation_range(max, min)         | Set the operation temperature range                   | TEMPerature:RANGe max,min                 | TEMPerature:RANGe max,min                 |
| get_default_operation_range()         | Get the default operation temperature range           | TEMPerature:DRANge?                       | N/A                                       |
| get_system_status()                   | Get the current system status                         | TEMPerature:STATus?                       | TEMPerature:STATus?                       |
| get_serial_number()                   | Get the system serial number                          | TEMPerature:SNUMber?                      | TEMPerature:SNUMber?                      |
| get_set_point_temperature()           | Get the set point (TSP) temperature                   | TEMPerature:SPOint?                       | TEMPerature:SPOint?                       |
| get_ramp_rate()                       | Get the current ramp rate                             | TEMPerature:RATe?                         | N/A                                       |
| get_ramp_rate_range()                 | Get the range of the ramp rate                        | TEMPerature:RTRange?                      | N/A                                       |
| get_power()                           | Get the current power value                           | TEMPerature:POWer?                        | N/A                                       |
| get_powerboard_temperature()          | Get the current powerboard RTD temperature            | TEMPerature:TP?                           | N/A                                       |
| get_error()                           | Get the current error                                 | TEMPerature:ERRor?                        | N/A                                       |
| get_operating_slave()                 | Get the operating slave                               | TEMPerature:OPSLave?                      | TEMPerature:OPSLave?                      |
| set_operating_slave(slave)            | Set the operating slave                               | TEMPerature:OPSLave slave                 | TEMPerature:OPSLave slave                 |
| get_slave_count()                     | Get the number of connected slaves                    | TEMPerature:SLAVes?                       | TEMPerature:SLAVes?                       |
| purge(delay, hold)                    | Complete a gas purge for the specified duration       | TEMPerature:PURGe delay,hold              | TEMPerature:PURGe delay,hold              |
| get_pv_unit_type()                    | Get unit type of PV                                   | TEMPerature:TCUNit?                       | N/A                                       |
| get_mv_unit_type()                    | Get unit type of MV                                   | TEMPerature:TMUNit?                       | N/A                                       |
| get_precision()                       | Get the decimal precision of PV and MV                | TEMPerature:PRECision?                    | N/A                                       |

7 additional functions have been implemented as well:

| Python Function               | Usage                                                   |
|:----------------------------: | :-----------------------------------------------------: |
| hold_check()                  | Execute hold function with operation range check; automatically stop controller if set value is out of range |
| ramp_check()                  | Execute ramp function with operation/rate range check; automatically stop controller if set value is out of range |
| rpp_check()                   | Execute rpp function with power range check; automatically stop controller if set value is out of range |
| get_process_variable()        | Get the process variable of the current operating slave |
| get_monitor_value()           | Get the monitor value of the current operating slave    |
| get_protection_sensor()       | Get the protection sensor value of the current operating slave |
| get_power_range()             | Get the power range                                     |
| is_in_power_range(pp)         | Check if pp value is in power range                     |
| is_in_ramp_rate_range(pp)     | Check if rt value is in ramp rate range                 |
| is_in_operation_range(temp)   | Check if temp value is in operation range               |

More information on the Python temperature commands can be found in the temperature.py and pid.py files.

#### PID Commands
There are a total of 3 SCPI PID commands implemented as Python functions in this library. Note that these commands only work with MK2000B models.

| Python Function                       | Usage                                                 | MK2000B SCPI Command                      |
|:----------------------------:         | :---------------------------------------:             | :---------------------------:             |
| get_current_pid()                     | Get current PID value                                 | TEMPerature:PID?                          |
| get_pid(state, index)                 | Get PID at specified table and index                  | TEMPerature:GPID state,index              |
| set_pid(state, index, temp, p, i, d)  | Set PID at specified table and index                  | TEMPerature:SPID state,index,temp,p,i,d   |

1 additional function has been implemented as well:

| Python Function               | Usage                                                   |
|:----------------------------: | :-----------------------------------------------------: |
| is_valid_pid_index(i)         | Check if pid index is valid                             |

#### Profile Commands

There are a total of 13 SCPI profile commands implemented as Python functions in this library. Note that these commands only work with MK2000B models.

| Python Function                       | Usage                                                     | MK2000B SCPI Command              |
|:----------------------------:         | :---------------------------------------:                 | :---------------------------:     |
| get_profile_state()                   | Get the current profile state                             | PROFile:RTSTate?                  |
| start_profile(p)                      | Start the selected profile.                               | PROFile:STARt p                   |
| pause_profile()                       | Pauses the currently running profile                      | PROFile:PAUSe                     |
| resume_profile()                      | Resumes the current profile                               | PROFile:RESume                    |
| stop_profile()                        | Stops the current profile                                 | PROFile:STOP                      |
| delete_profile(p)                     | Delete the selected profile                               | PROFile:EDIT:PDELete p            |
| delete_profile_item(p, i)             | Delete the selected profile item                          | PROFile:EDIT:IDELete p,i          |
| insert_profile_item(p, i, c, b1, b2)  | Insert the selected item into the selected profile        | PROFile:EDIT:IINSert p,i,c,b1,b2  |
| set_profile_item(p, i, c, b1, b2)     | Set the selected item in the selected profile             | PROFile:EDIT:IEDit p,i,c,b1,b2    |
| get_profile_item(p, i)                | Get the selected item from the selected profile           | PROFile:EDIT:IREad p,i            |
| get_profile_item_count(p)             | Get the number of items in the selected profile           | PROFile:EDIT:ICount p             |
| get_profile_name(p)                   | Get the profile name of the selected profile              | PROFile:EDIT:GNAMe p              |
| set_profile_name(p, name)             | Set the profile name of the selected profile              | PROFile:EDIT:SNAMe p,"name"       |

3 additional functions have been implemented as well:

| Python Function               | Usage                                                   |
|:----------------------------: | :-----------------------------------------------------: |
| add_profile_item(p, i, c, b1, b2) | Add item to the end of the profile                  |
| is_valid_profile(p)          | Check if selected profile is valid                       |
| is_valid_item_index(i)       | Check if selected item index is valid                    |

More information on the Python profile commands can be found in profile.py.

#### Compatibility
The compatibility for all Python functions is listed below. Python functions that are not supported by their respective devices will raise a NotImplementedError when called.

| Category                              | Python Function                       | MK2000B Support                     | MK2000VCP Support                   | Notes                               |
|:----------------------------:         | :---------------------------:         | :---------------------------:       | :---------------------------:       | :---------------------------:       |
| Temperature                           | get_system_information()              | Supported                           | Supported*                          | *MK2000VCP utilizes a different raw return string, so the function uses get_serial_number() to return the serial number in addition to the other information provided. |
| Temperature                           | get_runtime_information()             | Supported                           | Supported*                          | *MK2000VCP has no error reporting functionality, and will return -1 for the error code. |
| Temperature                           | get_process_variables()               | Supported                           | Supported                           |                                     |
| Temperature                           | get_monitor_values()                  | Supported                           | Supported                           |                                     |
| Temperature                           | get_protection_sensors()              | Supported                           | Not Supported                       |                                     |
| Temperature                           | hold(tsp)                             | Supported                           | Supported                           |                                     |
| Temperature                           | ramp(tsp, rt)                         | Supported                           | Supported                           |                                     |
| Temperature                           | rpp(pp)                               | Supported                           | Supported                           |                                     |
| Temperature                           | stop()                                | Supported                           | Supported                           |                                     |
| Temperature                           | get_cooling_heating_status()          | Supported                           | Supported                           |                                     |
| Temperature                           | set_cooling_heating_status(status)    | Supported                           | Supported                           |                                     |
| Temperature                           | get_stage_range()                     | Supported                           | Not Supported                       |                                     |
| Temperature                           | get_operation_range()                 | Supported                           | Supported                           |                                     |
| Temperature                           | set_operation_range(max, min)         | Supported                           | Supported                           |                                     |
| Temperature                           | get_default_operation_range()         | Supported                           | Not Supported                       |                                     |
| Temperature                           | get_system_status()                   | Supported                           | Supported                           |                                     |
| Temperature                           | get_serial_number()                   | Supported                           | Supported                           |                                     |
| Temperature                           | get_set_point_temperature()           | Supported                           | Supported                           |                                     |
| Temperature                           | get_ramp_rate()                       | Supported                           | Supported*                          | *MK2000VCP has no dedicated ramp rate SCPI query, so the function uses get_runtime_information() to retrieve the ramp rate value. |
| Temperature                           | get_ramp_rate_range()                 | Supported                           | Not Supported                       |                                     |
| Temperature                           | get_power()                           | Supported                           | Supported*                          | *MK2000VCP has no dedicated power percent SCPI query, so the function uses get_runtime_information() to retrieve the power percent value. |
| Temperature                           | get_powerboard_temperature()          | Supported                           | Not Supported                       |                                     |
| Temperature                           | get_error()                           | Supported                           | Not Supported                       |                                     |
| Temperature                           | get_operating_slave()                 | Supported                           | Supported                           |                                     |
| Temperature                           | set_operating_slave(slave)            | Supported                           | Supported                           |                                     |
| Temperature                           | get_slave_count()                     | Supported                           | Supported                           |                                     |
| Temperature                           | purge(delay, hold)                    | Supported                           | Supported                           |                                     |
| Temperature                           | get_pv_unit_type()                    | Supported                           | Not Supported                       |                                     |
| Temperature                           | get_mv_unit_type()                    | Supported                           | Not Supported                       |                                     |
| Temperature                           | get_precision()                       | Supported                           | Not Supported                       |                                     |
| Temperature                           | hold_check()                          | Supported                           | Supported                           |                                     |
| Temperature                           | ramp_check()                          | Supported                           | Supported                           |                                     |
| Temperature                           | rpp_check()                           | Supported                           | Supported                           |                                     |
| Temperature                           | get_process_variable()                | Supported                           | Supported                           |                                     |
| Temperature                           | get_monitor_value()                   | Supported                           | Supported                           |                                     |
| Temperature                           | get_protection_sensor()               | Supported                           | Supported                           |                                     |
| Temperature                           | get_power_range()                     | Supported                           | Supported                           |                                     |
| Temperature                           | is_in_power_range(pp)                 | Supported                           | Supported                           |                                     |
| Temperature                           | is_in_ramp_rate_range(pp)             | Supported                           | Not Supported                       |                                     |
| Temperature                           | is_in_operation_range(temp)           | Supported                           | Supported                           |                                     |
| PID                                   | get_current_pid()                     | Supported                           | Not Supported                       |                                     |
| PID                                   | get_pid(state, index)                 | Supported                           | Not Supported                       |                                     |
| PID                                   | set_pid(state, index, temp, p, i, d)  | Supported                           | Not Supported                       |                                     |
| PID                                   | is_valid_pid_index(i)                 | Supported                           | Not Supported                       |                                     |
| Profile                               | get_profile_state()                   | Supported                           | Not Supported                       |                                     |
| Profile                               | start_profile(p)                      | Supported                           | Not Supported                       |                                     |
| Profile                               | pause_profile()                       | Supported                           | Not Supported                       |                                     |
| Profile                               | resume_profile()                      | Supported                           | Not Supported                       |                                     |
| Profile                               | stop_profile()                        | Supported                           | Not Supported                       |                                     |
| Profile                               | delete_profile(p)                     | Supported                           | Not Supported                       |                                     |
| Profile                               | delete_profile_item(p, i)             | Supported                           | Not Supported                       |                                     |
| Profile                               | insert_profile_item(p, i, c, b1, b2)  | Supported                           | Not Supported                       |                                     |
| Profile                               | set_profile_item(p, i, c, b1, b2)     | Supported                           | Not Supported                       |                                     |
| Profile                               | get_profile_item(p, i)                | Supported                           | Not Supported                       |                                     |
| Profile                               | get_profile_item_count(p)             | Supported                           | Not Supported                       |                                     |
| Profile                               | get_profile_name(p)                   | Supported                           | Not Supported                       |                                     |
| Profile                               | set_profile_name(p, name)             | Supported                           | Not Supported                       |                                     |
| Profile                               | add_profile_item(p, i, c, b1, b2)     | Supported                           | Not Supported                       |                                     |
| Profile                               | is_valid_profile(p)                   | Supported                           | Not Supported                       |                                     |
| Profile                               | is_valid_item_index(i)                | Supported                           | Not Supported                       |                                     |

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

All enums can be seen in the constants.py file and correspond with their respective integer values in the SCPI command guide. If a function requires an enum, it will be mentioned in the docstring of the function.

## Examples
There are a total of 6 examples currently included with this repository.

### basic_hold.py

This example follows a very basic process: initializing the controller, executing a HOLD command, waiting for a specified amount of time, then checking the TSP value and returning the PV value. After completing the previous actions, the program stops the HOLD command and disconnects from the controller.

### consecutive_ramp.py

This example takes a list of TSP and RT values, using them to execute several RAMP commands in sucession. After a RAMP is executed, the program calculates the prospective amount of time it will take for the RAMP to finish executing based on the current temperature and TSP temperature, then wait that duration of time before executing the next RAMP.

### controller_info.py

This example prints out various information about the controller, including the connection status, runtime information, and ramp rate range. The program queries each of these commands a specified amount of times, with a specified delay.

### profile_hold.py

This example creates and stores a profile to an empty profile slot or a profile location specified by the user. The profile itself consists of alternating HOLD and WAIT commands, in which the profile will HOLD and WAIT at specified temperatures and durations.

### profile_transfer.py

This example reads a specified profile from the controller and converts it into a Python program using temperature commands instead of profile commands. The functionality of this program will NOT be identical to the profile on the controller due to the implementation of Delta T and Duration on the controller. Instead, the program uses the variable PRECISION to indicate when it should move on to the next item in the profile.

### profile_copy.py

This example reads a specified profile from the controller and converts it into a Python program that uses profile commands to reconstruct the profile. The functionality of a profile created from this program is identical since all commands are preserved.
