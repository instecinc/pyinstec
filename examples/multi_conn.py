from typing import List
import instec


addresses = instec.MK2000B.get_ethernet_controllers()
print(addresses)

controllers: List[instec.MK2000B] = []

for address in addresses:
    controllers.append(instec.MK2000B(serial_num=address[0]))

for controller in controllers:
    controller.is_connected()

for controller in controllers:
    controller.connect()
    print(f'PV of Controller at IP {controller._controller._controller_address}: {controller.get_process_variable()}')