"""This example reads an existing profile and
converts it into a python script.
"""


import instec
import os

import instec.profile


MODE = instec.mode.USB
BAUD = 38400
PORT = 'COM3'

controller = instec.instec(MODE, BAUD, PORT)
controller.connect()

selected_profile = int(input('Select profile: '))

name = controller.get_profile_name(selected_profile).strip()
name.replace(' ', '_')
filename = f'transferred_profile_{selected_profile}_{name}.py'
file = None

try:
    print(f'Creating file {filename}')
    file = open(filename, 'x')
except OSError:
    print('File already exists')
    confirm = input('Replace file (Y/n)? ')
    if 'Y'.casefold() == confirm.casefold():
        os.remove(filename)
        file = open(filename, 'x')
    elif 'n'.casefold() == confirm.casefold():
        print('Exiting program')
        exit(0)
    else:
        exit(1)

file.write(f'''
import time
import instec


controller = instec.instec(instec.mode.{'USB' if MODE == instec.mode.USB else 'ETHERNET'}, {BAUD}, '{PORT}')
controller.connect()
''')

indent = ''

for i in range(controller.get_profile_item_count(selected_profile)):
    item = controller.get_profile_item(selected_profile, i)
    command = ''
    match(item[0]):
        case instec.profile_item.HOLD:
            command = f'controller.hold({item[1]})'
        case instec.profile_item.RAMP:
            command = f'controller.ramp({item[1]}, {item[2]})'
        case instec.profile_item.WAIT:
            command = f'time.sleep({item[1] * 60})'
        case instec.profile_item.LOOP_BEGIN:
            command = f'for i{i} in range({int(item[1])}):'
        case instec.profile_item.LOOP_END:
            indent = indent[:-4]
        case instec.profile_item.PURGE:
            command = f'controller.purge({item[1]}, {item[2]})'
        case instec.profile_item.STOP:
            command = 'controller.stop()'
        case instec.profile_item.HEATING_AND_COOLING:
            command = 'controller.set_cooling_heating_status(instec.temperature_mode.HEATING_AND_COOLING)'
        case instec.profile_item.HEATING_ONLY:
            command = 'controller.set_cooling_heating_status(instec.temperature_mode.HEATING_ONLY)'
        case instec.profile_item.RPP:
            command = f'controller.rpp({item[1]})'
        case instec.profile_item.COOLING_ONLY:
            command = 'controller.set_cooling_heating_status(instec.temperature_mode.COOLING_ONLY)'
    file.write(f'''
{indent}{command}''')
    if item[0] == instec.profile_item.LOOP_BEGIN:
        indent += '    '

file.write('''

controller.disconnect()
''')

print('Profile created')
file.close()
