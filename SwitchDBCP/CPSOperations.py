import cps_utils
import cps_object
import socket
import netaddr as net
import cps
import struct

import time

from .Utils import Utils
from SwitchDBCP.Interface import Interface


class cps_operations:

    @staticmethod
    def getIfIndexFromName(name):
        """

        :param name:
        :return:
        """
        list = []
        # Obtain a list with objects from dell-base-if-cmn/if/interfaces/interface
        cps.get([cps.key_from_name('target', 'dell-base-if-cmn/if/interfaces/interface')], list)

        # Ignore the first entry
        for entry in list[1:]:
            # Construct a new object for each entry
            get_obj = cps_object.CPSObject(obj=entry)
            if (get_obj.get_attr_data("if/interfaces/interface/name") == name):
                return get_obj.get_attr_data("dell-base-if-cmn/if/interfaces/interface/if-index")


    @staticmethod
    def setInterfaceIpAddress(if_name, ip_addr, pfix_len):
        """

        :param if_name:
        :param ip_addr:
        :param pfix_len:
        :return:
        """

        # Populate the attributes for the CPS Object
        # From the arguments
        if_index = cps_operations.getIfIndexFromName(if_name)
        ip_attributes = {"base-ip/ipv4/ifindex": if_index, "ip": ip_addr, "prefix-length": pfix_len}

        # Create CPS Object
        cps_utils.add_attr_type('base-ip/ipv4/address/ip', "ipv4")
        cps_obj = cps_utils.CPSObject('base-ip/ipv4/address', data=ip_attributes)

        # Create the CPS Transaction for object create
        cps_update = ('create', cps_obj.get())
        transaction = cps_utils.CPSTransaction([cps_update])

        # Verify return value
        ret = transaction.commit()
        if not ret:
            raise RuntimeError("Error changing interface ip address")
        Utils.cliLogger("CPSOPErations: Changed interface ip address: " + ip_addr, 0)


    @staticmethod
    def setInterfaceName():
        return 1

    @staticmethod
    def setInterfaceMAC():
        return 1

    @staticmethod
    def setInterfaceMTU():
        return 1

    @staticmethod
    def setInterfaceType():
        return 1

    @staticmethod
    def setInterfaceAdminLinkState(if_name, state):
        """

        :param if_name:
        :param state:
        :return:
        """
        # setInterfaceAdminLinkState('e101-002-0', 1)
        cps_obj = cps_object.CPSObject('dell-base-if-cmn/if/interfaces/interface')

        cps_obj.add_attr('if/interfaces/interface/name', if_name)

        cps_obj.add_attr('if/interfaces/interface/enabled', state)

        cps_update = {'change': cps_obj.get(), 'operation': 'set'}

        transaction = cps.transaction([cps_update])

        if not transaction:
            raise RuntimeError("Error change the interface state")

        Utils.cliLogger("CPSOPErations: Changed interface state: " + if_name + " to " + str(state), 0)

    @staticmethod
    def setInterfaceLinkSpeed():
        return 1

    @staticmethod
    def setSwitchId():
        return 1

    @staticmethod
    def setSwitchIp():
        return 1

    @staticmethod
    def setSwitchName():
        return 1

    @staticmethod
    def addIpv4RouteEntry(route_prefix, prefix_len, if_name, weight,next_hop):
        """

        :param ip_addr:
        :param ip_prefix:
        :param interface_name:
        :param metric:
        :return:
        """
        version = 'ipv4'

        obj = cps_utils.CPSObject('base-route/obj/entry')
        obj.add_attr("vrf-id", 0)

        # Ipv4 version
        obj.add_attr("af", socket.AF_INET)

        ip = net.IPNetwork(route_prefix)
        obj.add_attr_type("route-prefix", version)
        obj.add_attr("route-prefix", str(ip.network))
        obj.add_attr("prefix-len", int(prefix_len))

        # Next hops

        lst = ["nh-list", "0", "nh-addr"]
        obj.add_embed_attr(lst, str(next_hop))
        #ifindex = cps_operations.getIfIndexFromName(if_name)
        #lst = ["nh-list", "0", "ifindex"]
        #obj.add_embed_attr(lst, int(ifindex))
        lst = ["nh-list", "0", "weight"]
        obj.add_embed_attr(lst, int(weight))

        obj.add_attr("nh-count", 1)
        # Create transaction
        cps_update = ('create', obj.get())
        transaction = cps_utils.CPSTransaction([cps_update])
        # Verify return value
        ret = transaction.commit()
        if not ret:
            #raise RuntimeError("Error creating Route")
            print("[CPSOperations]Error Creating Route")
            return

        Utils.timeLogger()
        Utils.cliLogger("New route: " + str(route_prefix) + "/" + str(prefix_len) + " interface: " + str(if_name) + " metric " + str(weight),0)


        # addIpv4RouteEntry('10.1.1.0',24,"e101-001-0",100)

    @staticmethod
    def deleteIpv4RouteEntry(route_prefix, prefix_len):
        """
        Delete and IPv4 route entry
        :param ip_addr: The ip address of the route.
        :param ip_prefix:
        :return:
        """
        # deleteIpv4RouteEntry("10.1.1.0", 24)
        ip_version = "ipv4"

        obj = cps_utils.CPSObject('base-route/obj/entry')

        obj.add_attr("vrf-id", 0)

        obj.add_attr("af", socket.AF_INET)

        ip = net.IPNetwork(route_prefix)

        obj.add_attr_type("route-prefix", ip_version)
        obj.add_attr("route-prefix", str(ip.network))
        obj.add_attr("prefix-len", int(prefix_len))

        cps_update = ('delete', obj.get())
        transaction = cps_utils.CPSTransaction([cps_update])

        ret = transaction.commit()

        if not ret:
            raise RuntimeError("Error   deleting   Route")

        Utils.cliLogger("CPSOPErations: Deleted route: " + route_prefix + "/" + str(prefix_len),0)

    @staticmethod
    def getAllInterfacesData():
        """
        Acquire all current interfaces data.
        :return:  A list of Interface objects.
        """

        list = []
        interfaces = []
        # Obtain a list with objects from dell-base-if-cmn/if/interfaces/interface
        cps.get([cps.key_from_name('target', 'dell-base-if-cmn/if/interfaces/interface')], list)

        # Ignore the first entry
        for entry in list[1:]:

            # Construct a new object for each entry
            get_obj = cps_object.CPSObject(obj=entry)

            if_name = get_obj.get_attr_data("if/interfaces/interface/name")
            type = get_obj.get_attr_data("if/interfaces/interface/type")
            enabled = get_obj.get_attr_data("if/interfaces/interface/enabled")
            phys_address = get_obj.get_attr_data("dell-if/if/interfaces/interface/phys-address")
            mtu = get_obj.get_attr_data("dell-if/if/interfaces/interface/mtu")

            Utils.cliLogger("Name: " + if_name,1)
            Utils.cliLogger("Type: " + type,1)
            Utils.cliLogger("Enabled: " + str(enabled),1)
            Utils.cliLogger("phys-address: " + phys_address,1)
            Utils.cliLogger("MTU: " + str(mtu),1)
            #################### Get interface IP

            ip_addr= []
            cps.get([cps.key_from_name('target', 'base-ip/ipv4/address')], ip_addr)
            ip_address = ""
            prefix_length = ''
            for addr in ip_addr:

                get_aux_obj = cps_object.CPSObject(obj=addr)

                if (str(get_aux_obj.get_attr_data("base-ip/ipv4/name")) == if_name):

                    ip_address_hex = get_aux_obj.get_attr_data("base-ip/ipv4/address/ip")
                    prefix_length = get_aux_obj.get_attr_data("base-ip/ipv4/address/prefix-length")

                    # Some magic to convert from Hex-IP
                    ip_address = socket.inet_ntoa(struct.pack("<L", int(ip_address_hex,16)))
                    ip_address = '.'.join(str(ip_address).split(".")[::-1])


                    Utils.cliLogger("IP: " + str(ip_address), 1)
                    Utils.cliLogger("IP: " + str(prefix_length), 1)
            ###################
            aux_list = []
            # Get from dell-base-if-cmn/if/interfaces-state/interface
            cps.get([cps.key_from_name('observed', 'dell-base-if-cmn/if/interfaces-state/interface')], aux_list)
            # Ignore the first entry
            for aux_entry in aux_list[1:]:
                # Construct a new object for each entry

                get_aux_obj = cps_object.CPSObject(obj=aux_entry)

                if (get_aux_obj.get_attr_data("if/interfaces-state/interface/name") == get_obj.get_attr_data(
                        "if/interfaces/interface/name")):

                    oper_status = get_aux_obj.get_attr_data("if/interfaces-state/interface/oper-status")
                    speed = get_aux_obj.get_attr_data("if/interfaces-state/interface/speed")

                    Utils.cliLogger("oper-status: " + str(oper_status),1)
                    Utils.cliLogger("speed: " + str(speed),1)


            interface = Interface(if_name, type,enabled,phys_address,mtu,oper_status,speed,ip_address,prefix_length)
            interfaces.append(interface)
        return interfaces


    @staticmethod
    def getChassisMac():
        """

        :return: The physical address of the switch chassis.
        """
        list = []
        # Obtain a list with objects from dell-base-if-cmn/if/interfaces/interface
        cps.get([cps.key_from_name('target', 'base-pas/chassis')], list)

        # Ignore the first entry
        for entry in list:
            # Construct a new object for each entry
            get_obj = cps_object.CPSObject(obj=entry)

            phys_address = get_obj.get_attr_data("base_mac_addresses")
            Utils.cliLogger("Chassis MAC: " + phys_address,1)
            return phys_address
