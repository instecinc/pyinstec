"""This example reads an existing profile and
converts it into a python script.
"""


import instec
import os
import instec.profile


MODE = instec.mode.USB      # Connection mode
BAUD = 38400                # Baud rate for USB mode
PORT = 'COM3'               # Port for USB mode
PRECISION = 0.1             # Required precision of TSP/PP before moving to next instruction


# Initialize controller and connect
controller = instec.MK2000(MODE, BAUD, PORT)
controller.connect()

# Select profile
selected_profile = int(input('Select profile: '))

# Create and set filepath for new file
name = controller.get_profile_name(selected_profile).strip()
name.replace(' ', '_')
base_path = 'profiles'
file_name = f'transferred_profile_{selected_profile}_{name}.py'
file_path = os.path.join(base_path, file_name)
file = None

# Try to create/modify existing file
try:
    print(f'Creating file {file_name}')
    if not os.path.exists(os.path.join(base_path)):
        os.mkdir(os.path.join(base_path))
    file = open(file_path, 'x')
except OSError as error:
    print(f'File already exists {error}')
    confirm = input('Replace file (Y/n)? ')
    if 'Y'.casefold() == confirm.casefold():
        os.remove(file_path)
        file = open(file_path, 'x')
    elif 'n'.casefold() == confirm.casefold():
        print('Exiting program')
        exit(0)
    else:
        exit(1)

# Write controller initialization to file
file.write(f'''
import time
import instec


controller = instec.MK2000(instec.mode.{'USB' if MODE == instec.mode.USB else 'ETHERNET'}, {BAUD}, '{PORT}')
controller.connect()
''')

indent = ''

# Iterate through all items in profile and add to file
for i in range(controller.get_profile_item_count(selected_profile)):
    item = controller.get_profile_item(selected_profile, i)
    commands = ('',)
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
    for command in commands:
        file.write(f'''
{indent}{command}''')
    if item[0] == instec.profile_item.LOOP_BEGIN:
        indent += '    '

file.write('''

controller.disconnect()
''')

print('Profile created')
file.close()
