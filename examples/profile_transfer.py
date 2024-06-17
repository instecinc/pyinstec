"""Python program that reads an existing profile off of
the controller and converts it into a python script that uses
temperature commands instead of profile commands.

The functionality of the script is NOT identical to running
a profile on the controller. The controller uses Delta T and
Duration to determine when to move on to the next item in a
profile, but the generated script will ONLY delay until the
utilized temperature control command has reached within PRECISION
amount of the desired value.
"""


import instec
import os


# Variables for setting up the controller
MODE = instec.mode.USB      # Connection mode
BAUD = 38400                # Baud rate for USB mode
PORT = 'COM3'               # Port for USB mode

# Initialize controller and connect
print('Connecting to the controller')
controller = instec.MK2000(MODE, BAUD, PORT)
controller.connect()

# Required precision of TSP/PP before moving to next instruction
PRECISION = 0.1             # In °C or %

# Select profile
selected_profile = int(input('Select profile: '))

# Create and set filepath for new file
name = controller.get_profile_name(selected_profile).strip()
name.replace(' ', '_')
base_path = 'profiles'
file_name = f'transfer_profile_{selected_profile}_{name}.py'
file_path = os.path.join(base_path, file_name)

# Create file variable
file = None

# Try to create/modify existing file
try:
    print(f'Creating file {file_name}')

    # If the path does not exist, create one
    if not os.path.exists(os.path.join(base_path)):
        os.mkdir(os.path.join(base_path))

    # Create the file
    file = open(file_path, 'x')
except OSError:
    # The file already exists, confirm with user to
    # remove previous version
    print('File already exists')
    confirm = input('Replace file (Y/n)? ')
    if 'Y'.casefold() == confirm.casefold():
        # Remove old version and add new one
        os.remove(file_path)
        file = open(file_path, 'x')
    elif 'n'.casefold() == confirm.casefold():
        print('Exiting program')
        exit(0)
    else:
        exit(1)

# Write controller initialization to file
file.write(f'''
"""Generated profile program converting {name} to temperature commands.
"""


import time
import instec


controller = instec.MK2000(instec.mode.{'USB' if MODE == instec.mode.USB else 'ETHERNET'}, {BAUD}, '{PORT}')
controller.connect()
''')

# Indent variable to maintain proper indentation after loops
indent = ''

# Iterate through all items in profile and add different functions to the file
# depending on the item.
for i in range(controller.get_profile_item_count(selected_profile)):
    item = controller.get_profile_item(selected_profile, i)
    commands = ('',)
    # Determine item instruction type and select commands accordingly
    match(item[0]):
        case instec.profile_item.HOLD:
            commands = (f'controller.hold({item[1]})',
                        'pv = controller.get_process_variables()[controller.get_operating_slave()]',
                        f'while abs(pv - {item[1]}) > {PRECISION}:',
                        '    pv = controller.get_process_variables()[controller.get_operating_slave()]',)
        case instec.profile_item.RAMP:
            commands = (f'controller.ramp({item[1]}, {item[2]})',
                        'pv = controller.get_process_variables()[controller.get_operating_slave()]',
                        f'while abs(pv - {item[1]}) > {PRECISION}:',
                        '    pv = controller.get_process_variables()[controller.get_operating_slave()]',)
        case instec.profile_item.WAIT:
            commands = (f'time.sleep({item[1] * 60})',)
        case instec.profile_item.LOOP_BEGIN:
            commands = (f'for i{i} in range({int(item[1])}):',)
        case instec.profile_item.LOOP_END:
            indent = indent[:-4]
        case instec.profile_item.PURGE:
            commands = (f'controller.purge({item[1]}, {item[2]})',
                        f'time.sleep({item[1] + item[2]})',)
        case instec.profile_item.STOP:
            commands = ('controller.stop()',)
        case instec.profile_item.HEATING_AND_COOLING:
            commands = ('controller.set_cooling_heating_status(instec.temperature_mode.HEATING_AND_COOLING)',)
        case instec.profile_item.HEATING_ONLY:
            commands = ('controller.set_cooling_heating_status(instec.temperature_mode.HEATING_ONLY)',)
        case instec.profile_item.RPP:
            controller.get_power()
            commands = (f'controller.rpp({item[1]})',
                        'pp = controller.get_power()',
                        f'while abs(pp - {item[1]}) > {PRECISION / 100.0}:',
                        '    pp = controller.get_power()',)
        case instec.profile_item.COOLING_ONLY:
            commands = ('controller.set_cooling_heating_status(instec.temperature_mode.COOLING_ONLY)',)

    # Write commands to file
    for command in commands:
        file.write(f'''
{indent}{command}''')
    if item[0] == instec.profile_item.LOOP_BEGIN:
        indent += '    '

# Write controller disconnect to file
file.write('''

controller.disconnect()
''')

print('Profile created')
file.close()

# Disconnect the controller
print('Disconnecting the controller')
controller.disconnect()
