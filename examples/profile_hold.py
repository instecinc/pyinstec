"""Python program that creates a profile consisting of
consecutive HOLD and WAIT commands.
"""

import instec


# Variables for setting up the controller
MODE = instec.mode.USB      # Connection mode
BAUD = 38400                # Baud rate for USB mode
PORT = 'COM3'               # Port for USB mode

# Initialize controller and connect
print('Connecting to the controller')
controller = instec.MK2000(MODE, BAUD, PORT)
controller.connect()

# Define temperature increment and wait time after each HOLD
INCREMENT = 20      # In °C
WAIT_TIME = 1       # In seconds

# Try to find empty profile to create new profile in
selected_profile = None
for i in range(5):
    if controller.get_profile_item_count(i) == 0:
        selected_profile = i
        break

print('All profiles are full' if selected_profile is None
      else f'Using profile {selected_profile}')

# If all profiles are not empty, choose a profile to delete
if selected_profile is None:
    selected_profile = int(input("Select profile: "))
    controller.delete_profile(selected_profile)

# Set the profile name
controller.set_profile_name(selected_profile, input("Set profile name: "))

# Set the max operation temperature
max = float(input("Set maximum operation temperature: "))

# Set the min operation temperature
min = float(input("Set minimum operation temperature: "))

controller.set_operation_range(max, min)

# Start counter at minimum temperature
count = min

# While the counter is less than the maximum temperature
while count < max:
    # Add a HOLD item to the profile at the counter temperature
    controller.add_profile_item(
        selected_profile, instec.profile_item.HOLD, count)

    # Add a WAIT item to the profile with the WAIT_TIME duration
    controller.add_profile_item(
        selected_profile, instec.profile_item.WAIT, WAIT_TIME)

    print(f"Added HOLD at {count} and WAIT for {WAIT_TIME} minutes")

    # Increment counter temperature
    count += INCREMENT

print("Profile created")

# Disconnect the controller
print('Disconnecting the controller')
controller.disconnect()
