from .Utils import Utils
from SwitchDBCP.Neighbour import Neighbour
import os
import json
import subprocess

class ExternalOperations:
    # Extract all the current neighbours
    #MANAGMENT_IF_NAME = 'eth0'
    @staticmethod
    def lldp_extractor():
        neighbours = []

        p = subprocess.Popen(["lldpcli", "show", "neighbor", "-f", "json"], stdout=subprocess.PIPE)
        output, err = p.communicate()

        data = json.loads(output)

        # Are there interfaces on the map?
        if "interface" not in data["lldp"]:
            return neighbours
        else:
            interfaces = data["lldp"]["interface"]
            # is there more then 1 interface?
            if isinstance(interfaces,list):
                for interface in interfaces:
                    if_name = interface.keys()[0]
                    chassis_name = interface[if_name]["chassis"].keys()[0]
                    if (chassis_name != "id"):  # Ignore id
                        age = interface[if_name]["age"]
                        mgmt_ip = interface[if_name]["chassis"][chassis_name]["mgmt-ip"][0]
                        remote_phys = interface[if_name]["chassis"][chassis_name]["id"]["value"]
                        remote_if_name = interface[if_name]["port"]["id"]["value"]
                        Utils.cliLogger("Interface name: " + if_name, 1)
                        Utils.cliLogger("    Managment IP :" + mgmt_ip, 1)
                        Utils.cliLogger("    Age: " + age, 1)
                        Utils.cliLogger("    Chassis name: " + chassis_name, 1)
                        neighbour = Neighbour(if_name, remote_phys,remote_if_name,"")
                        neighbours.append(neighbour)
            return neighbours



    @staticmethod
    def get_managment_network_ip():
        ipv4 = os.popen('ip addr show eth0').read().split("inet ")[1].split("/")[0]
        return ipv4


