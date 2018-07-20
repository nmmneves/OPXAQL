import uuid

from ControllerDBCP.DBoperations import DBoperations
from .Utils import Utils
from ControllerDBCP.Convergence import Routing

IF_OPER_STATUS_UP = 1
IF_OPER_STATUS_DOWN = 2

class Handler:
    def __init__(self):
        self.db_operations = DBoperations()

    def interface_neighbour_change(self):
        self.convergance()

    def interface_oper_status_change(self,interface_id):
        query = self.db_operations.GET_INTERFACE_OPER_STATUS_BY_NAME_ID
        args = (interface_id)
        results = self.db_operations.db_select_operation(query, args)
				
        for interface in results:
            oper_status = interface["operstatus"]

        if (oper_status == IF_OPER_STATUS_UP):
            return 
					
        self.log("Will delete all neighbour relations with interface: " + interface_id )

        query = self.db_operations.GET_NEIGHBOUR_SWITCH_RELATIONS_BY_INTERFACE
        args = (interface_id)
        results = self.db_operations.db_select_operation(query, args)
		
        for result in results:
            remote_phys_address = ''.join(chr(i) for i in result["physaddress"])
            remote_if_name = ''.join(chr(i) for i in result["remoteinterfacename"])
		
        query = self.db_operations.GET_ALL_SWITCHES_BY_PHYS_ADDRESS
        args = (remote_phys_address.replace(":", ""))
        switches = self.db_operations.db_select_operation(query, str(args))
		
        for result in switches:
            remote_switch_identifier = ''.join(chr(i) for i in result["identifier"])

        query2 = self.db_operations.GET_INTERFACE_BY_NAME_SWITCH

        queryargs2 = query2.format(remote_if_name,remote_switch_identifier)
        interfaces = self.db_operations.db_select_operation(queryargs2, '')
        for interface in interfaces:
                remote_interfaces_id = ''.join(chr(i) for i in interfaces[0]["identifier"])
        operations = []
		
        query2 = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID
        queryargs2 = query2.format(remote_interfaces_id)
        operations.append(queryargs2)
        self.db_operations.db_insert_operations(operations)
        operations = [] 
		
        query = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID
        queryargs = query.format(interface_id)
        operations.append(queryargs)
        self.db_operations.db_insert_operations(operations)

        self.convergance()

    def convergance(self):
        self.log("Convergence request received.")
        Routing.convergance(self.db_operations)

    def log(self,data):
        Utils.cliLogger("[DataHandler] "+ data,0)









