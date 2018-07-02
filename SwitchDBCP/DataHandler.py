import uuid

from SwitchDBCP.DBoperations import DBoperations
from SwitchDBCP.ExternalOperations import ExternalOperations
from SwitchDBCP.CPSOperations import cps_operations
from .Utils import Utils

class Handler:
    def __init__(self):
        self.db_operations = DBoperations()

    def get_if_id_from_name(self, if_name):
        """
        Queries and returns the UUID of an interface with specific name.
        :param if_name: An interface name.
        :return: The UUID of the switch or None if the interfaces does not exist in the model.
        """
        query = self.db_operations.GET_IFENTIFIER_FROM_NAME
        results = self.db_operations.db_select_operation(query, if_name)
        # If there is no result, this interface name does belong to the data model.
        # Might happen with the management network interface name
        if not results:
            return None
        else:
            if_identifier = ''.join(chr(i) for i in results[0]['identifier'])
            return if_identifier

    def get_switch_UUID(self):
        """
        Queries and returns the UUID of the switch.
        :return: The UUID of the switch
        """
        query = self.db_operations.GET_IFENTIFIER_FROM_SWITCH
        results = self.db_operations.db_select_operation(query, ())
        switch_uuid = ''.join(chr(i) for i in results[0]['identifier'])
        return switch_uuid



    def add_neighbour(self, if_name, phys_address,remote_if_name):
        """
        Add new neighbour to the database.
        :param if_name: The name of the interface with the neighbour operation.
        :param phys_address: The physical address of the neighbour.
        :return:
        """
        #Check neighbour presence
        query = self.db_operations.GET_NEIGHBOUR_COUNT_FROM_PHYSADDRESS
        phys_address_to_ascii = [ord(c) for c in phys_address]
        results = self.db_operations.db_select_operation(query, phys_address_to_ascii)

        # If the neighbour already exists, just add the reference.
        operations = []
        switch_id = self.get_switch_UUID()
        if not results:
            # Add new neighbour
            query1 = self.db_operations.INSERT_NEIGHBOUR
            queryargs = query1.format(phys_address,switch_id)
            operations.append(queryargs)

        # Add interface reference
        if_identifier = self.get_if_id_from_name(if_name)
		
        # If there is no result, this interface name does belong to the data model.
        # Might happen with the management network interface name
        if not if_identifier:
           return 0;
        query2 = self.db_operations.INSERT_INTERFACE_NEIGHBOUR
        queryargs2 = query2.format(if_identifier,phys_address,remote_if_name,switch_id)
        operations.append(queryargs2)
        self.db_operations.db_insert_operations(operations)
        self.log("Neighbour added to the database. Interface name: " + if_name + " Neighbour: "+ phys_address)
        return 1;


    def del_neighbour(self, if_name):
        """
        Delete neighbours reference to the interfaces on the database.
        :param if_name: The name of the interface with neighbour operation.
        :return:
        """

        # Delete just the relationship to the neighbour
        operations = []
        if_identifier = self.get_if_id_from_name(if_name)

        query = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID
        queryargs = query.format(if_identifier)
        operations.append(query)
        self.db_operations.db_insert_operations(operations)
        self.log("Neighbour reference deleted from the database. Interface name: " + if_name)


    def add_route(self,route_prefix,prefix_len,if_name,weight,next_hop):
        '''

        :param route_prefix:
        :param prefix_len:
        :param if_name:
        :param weight:
        :param next_hop:
        :return:
        '''
		
        cps_operations.addIpv4RouteEntry(route_prefix,prefix_len,if_name,weight,next_hop)


    def del_route(self,route_prefix,prefix_len):
        """

        :param route_prefix:
        :param prefix_len:
        :return:
        """
        cps_operations.deleteIpv4RouteEntry(route_prefix, prefix_len)

    def update_route(self, route_prefix, prefix_len, if_name, weight,next_hop):
        '''

        :param route_prefix:
        :param prefix_len:
        :param if_name:
        :param weight:
        :param next_hop:
        :return:
        '''

        cps_operations.addIpv4RouteEntry(route_prefix, prefix_len, if_name, weight,next_hop)
        cps_operations.deleteIpv4RouteEntry(route_prefix, prefix_len)


    def change_interface(self, interface):
        """
        Change interface data on the database.

        :param interface: An Interface object.
        :return:
        """
        operations = []
        if_identifier = self.get_if_id_from_name(interface.name)
        # Updating "oper-status" field only, for now.
        query = self.db_operations.UPDATE_INTERFACE_OPERSTATUS
        queryargs = query.format(interface.oper_status, if_identifier)
        operations.append(queryargs)
        #print("Operstatus data handler: ",queryargs)
        self.db_operations.db_insert_operations(operations)

        self.log("Interfaces changes added to the database. Operstatus changed to: " + str(interface.oper_status) + " of: " + if_identifier)



    def get_all_switch_data(self):
        """
        Get all current OPX switch data.
        :return:
        """
        querylist = []
        phys_address = cps_operations.getChassisMac()
        managment_network = ExternalOperations.get_managment_network_ip()
        query = self.db_operations.INSERT_SWITCH
        queryargs = query.format(str(uuid.uuid4()),"",phys_address,managment_network)
        querylist.append(queryargs)
        self.db_operations.db_insert_operations(querylist)
        self.log("Switch data added to the database.")


    def get_all_interface_data(self):
        """
        Get all current interface data from CPS api and insert it on the database.
        :return:
        """

        # Get switch UUID
        switch_uuid = self.get_switch_UUID()
        # Get interface data
        interfaces = cps_operations.getAllInterfacesData()
        for interface in interfaces:
            # Insert individually
            querylist = []

            if (interface.prefix_length==''):

                query =  self.db_operations.INSERT_INTERFACE_UNUSED
                queryargs = query.format(str(uuid.uuid4()), interface.name, interface.type, interface.enabled, interface.oper_status,
                        interface.phys_address, interface.speed, interface.mtu, switch_uuid, interface.ip)
            else:

                query = self.db_operations.INSERT_INTERFACE
                queryargs = query.format(str(uuid.uuid4()), interface.name, interface.type, interface.enabled, interface.oper_status,
                    interface.phys_address, interface.speed, interface.mtu, switch_uuid,interface.ip,interface.prefix_length)
            querylist.append(queryargs)

            self.db_operations.db_insert_operations(querylist)
        self.log("Interfaces data added to the database(Total of "+ str(len(interfaces)) +").")


    def get_all_current_neighbours(self):
        """
        Get all the current active neighbours data and insert it on the database.
        :return:
        """
        neighbourhood = ExternalOperations.lldp_extractor()
        numberneighbours = 0;
        for neighbour in neighbourhood:
            numberneighbours = numberneighbours + self.add_neighbour(neighbour.local_if,neighbour.remote_chassis_phys_addrs,neighbour.remote_if_name)
        self.log("Current neighbours added to the database(Total of " + str(numberneighbours) + ").")


    def log(self,data):
        Utils.cliLogger("[DataHandler] "+ data,0)

	""" def set_interface_ip(self,if_name,ip_addr,pfix_len):

    cps_operations.setInterfaceIpAddress(if_name, ip_addr, pfix_len)

    def set_interface_admin_state(self,if_name,enabled):
      
    cps_operations.setInterfaceAdminLinkState(if_name, enabled)"""






