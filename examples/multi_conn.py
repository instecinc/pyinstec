import sys
import os

# Run tests using local copy of library - comment this out if unnecessary
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
import instec


addresses = instec.MK2000.get_ethernet_controllers()
print(addresses)

controllers: List[instec.MK2000] = []

for address in addresses:
    controllers.append(instec.MK2000(serial_num=address[0]))

for controller in controllers:
    controller.is_connected()

for controller in controllers:
    controller.connect()
    print(f'PV of Controller at IP {controller._controller._controller_address}: {controller.get_process_variable()}')