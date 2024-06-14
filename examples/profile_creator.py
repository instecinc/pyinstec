import instec


INCREMENT = 20
WAIT_TIME = 1

MODE = instec.mode.USB      # Connection mode
BAUD = 38400                # Baud rate for USB mode
PORT = 'COM3'               # Port for USB mode

controller = instec.MK2000(MODE, BAUD, PORT)

controller.connect()

selected_profile = None
# Try to find empty profile
for i in range(5):
    if controller.get_profile_item_count(i) == 0:
        selected_profile = i
        break

print('All profiles are full' if selected_profile is None
      else f'Using profile {selected_profile}')

if selected_profile is None:
    selected_profile = int(input("Select profile: "))
    controller.delete_profile(selected_profile)

controller.set_profile_name(selected_profile, input("Set profile name: "))

max = float(input("Set maximum operation temperature: "))

min = float(input("Set minimum operation temperature: "))

controller.set_operation_range(max, min)

count = min

while count < max:
    controller.add_profile_item(
        selected_profile, instec.profile_item.HOLD, count)
    controller.add_profile_item(
        selected_profile, instec.profile_item.WAIT, WAIT_TIME)
    print(f"Added HOLD at {count} and WAIT for {WAIT_TIME} minutes")
    count += INCREMENT

print("Finished creating profile.")
controller.disconnect()
