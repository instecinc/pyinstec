"""Python program that reads an existing profile off of
the controller and converts it into a python script that
can recreate the profile on the controller.

The functionality of profile recreated by this program
should be IDENTICAL to the original script on retrieved
from the controller if parameters provided are valid.
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
name = controller.get_profile_name(selected_profile)
name = name.strip().replace(' ', '_')
base_path = 'profiles'
file_name = f'copy_profile_{selected_profile}_{name}.py'
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
"""Generated profile program converting {name} to profile commands.
"""


import instec


controller = instec.MK2000(instec.mode.{'USB' if MODE == instec.mode.USB else 'ETHERNET'}, {BAUD}, '{PORT}')
controller.connect()

PROFILE = {selected_profile}

controller.delete_profile(PROFILE)

controller.set_profile_name('{name}')
''')
# Iterate through all items in profile and add different functions to the file
# depending on the item.
for i in range(controller.get_profile_item_count(selected_profile)):
    item = controller.get_profile_item(selected_profile, i)

    # Write commands to file
    file.write(f'''
controller.add_profile_item(PROFILE, instec.{item[0]}, {item[1]}, {item[2]})''')

# Write controller disconnect to file
file.write('''

controller.disconnect()
''')

print('Profile created')
file.close()

# Disconnect the controller
print('Disconnecting the controller')
controller.disconnect()
