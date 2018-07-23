import uuid

from SwitchDBCP.DBoperations import DBoperations
from SwitchDBCP.ExternalOperations import ExternalOperations
from SwitchDBCP.CPSOperations import cps_operations
from .Utils import Utils

class Handler:
    def __init__(self):
        self.db_operations = DBoperations()

    def get_if_id_from_name(self, if_name,switch_id):
        query = self.db_operations.GET_IDENTIFIER_FROM_NAME_AND_SWITCH
        queryargs = query.format(if_name,switch_id)
        results = self.db_operations.db_select_operation(queryargs,'')
        if not results:
            return None
        else:
            if_identifier = ''.join(chr(i) for i in results[0]['identifier'])
            return if_identifier


    def get_switch_UUID(self):
        query = self.db_operations.GET_IDENTIFIER_FROM_SWITCH
        results = self.db_operations.db_select_operation(query, ())
        switch_uuid = ''.join(chr(i) for i in results[0]['identifier'])
        return switch_uuid



    def add_neighbour(self, if_name, phys_address,remote_if_name):
        query = self.db_operations.GET_NEIGHBOUR_COUNT_FROM_PHYSADDRESS
        phys_address_to_ascii = [ord(c) for c in phys_address]
        results = self.db_operations.db_select_operation(query, phys_address_to_ascii)

        # If the neighbour already exists, just add the reference.
        operations = []
        switch_id = self.get_switch_by_physaddres()
        if not results:
            query1 = self.db_operations.INSERT_NEIGHBOUR
            queryargs = query1.format(phys_address,switch_id)
            operations.append(queryargs)

        if_identifier = self.get_if_id_from_name(if_name,switch_id)
		
        if not if_identifier:
           return 0;
        query2 = self.db_operations.INSERT_INTERFACE_NEIGHBOUR
        queryargs2 = query2.format(if_identifier,phys_address,remote_if_name,switch_id)
        operations.append(queryargs2)
        self.db_operations.db_insert_operations(operations)
        self.log("Neighbour added to the database. Interface name: " + if_name + " Neighbour: "+ phys_address)
        return 1;


    def del_neighbour(self, if_name):

        # Delete just the relationship to the neighbour
        operations = []
        query = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID
        switch_id = self.get_switch_by_physaddres()
        if_identifier = self.get_if_id_from_name(if_name,switch_id)
        queryargs = query.format(if_identifier)
        operations.append(query)
        self.db_operations.db_insert_operations(operations)
        self.log("Neighbour reference deleted from the database. Interface name: " + if_name)


    def add_route(self,route_prefix,prefix_len,if_name,weight,next_hop):

        cps_operations.addIpv4RouteEntry(route_prefix,prefix_len,if_name,weight,next_hop)


    def del_route(self,route_prefix,prefix_len):

        cps_operations.deleteIpv4RouteEntry(route_prefix, prefix_len)

    def update_route(self, route_prefix, prefix_len, if_name, weight,next_hop):
	
        cps_operations.deleteIpv4RouteEntry(route_prefix, prefix_len)
        cps_operations.addIpv4RouteEntry(route_prefix, prefix_len, if_name, weight,next_hop)

    def change_interface(self, interface):

        operations = []
		#Extra code to deal with full replication
        query = self.db_operations.GET_IDENTIFIER_FROM_NAME_AND_SWITCH
        ownid = self.get_switch_by_physaddres()
        queryargs = query.format(interface.name,ownid)
        results = self.db_operations.db_select_operation(queryargs,'')
        if_identifier = ''.join(chr(i) for i in results[0]['identifier'])
        #----------------------------------------------------------------
        query = self.db_operations.UPDATE_INTERFACE_OPERSTATUS
        queryargs = query.format(interface.oper_status, if_identifier)
        operations.append(queryargs)
        self.db_operations.db_insert_operations(operations)
        Utils.timeLogger("DataHandler| Database Insertion: ")
        self.log("Interfaces changes added to the database. Operstatus changed to: " + str(interface.oper_status) + " of: " + if_identifier)

    def get_all_switch_data(self):
	
        querylist = []
        phys_address = cps_operations.getChassisMac()
        managment_network = ExternalOperations.get_managment_network_ip()
        query = self.db_operations.INSERT_SWITCH
        queryargs = query.format(str(uuid.uuid4()),"",phys_address,managment_network)
        querylist.append(queryargs)
        self.db_operations.db_insert_operations(querylist)
        self.log("Switch data added to the database.")
    
    #(Extra code)This if is added to solve the problem of full replication
    def get_switch_by_physaddres(self):
        phys_address = cps_operations.getChassisMac()
        query = self.db_operations.GET_IDENTIFIER_FROM_SWITCH_BY_PHYSADDRESS
        result = self.db_operations.db_select_operation(query,phys_address)
        identifier = ''.join(chr(i) for i in result[0]['identifier'])
        return identifier
    #-----------------------------------------------------------------

    def get_all_interface_data(self):
        switch_uuid = self.get_switch_by_physaddres()
        interfaces = cps_operations.getAllInterfacesData()
        for interface in interfaces:
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

        neighbourhood = ExternalOperations.lldp_extractor()
        numberneighbours = 0;
        for neighbour in neighbourhood:
            numberneighbours = numberneighbours + self.add_neighbour(neighbour.local_if,neighbour.remote_chassis_phys_addrs,neighbour.remote_if_name)
        self.log("Current neighbours added to the database(Total of " + str(numberneighbours) + ").")


    def log(self,data):
        Utils.cliLogger("[DataHandler] "+ data,0)