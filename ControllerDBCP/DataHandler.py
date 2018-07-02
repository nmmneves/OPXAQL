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

        #Did the interface went UP or DOWN
        query = self.db_operations.GET_INTERFACE_OPER_STATUS_BY_NAME_ID
        args = (interface_id)
        results = self.db_operations.db_select_operation(query, args)
        print("Controller data handler OPER STATUS change results: ",results)
        for interface in results:  # Has just one
            oper_status = interface["operstatus"]

        if (oper_status == IF_OPER_STATUS_UP):
            return #We must ignore IF coming up

        self.log("Will delete all neighbour relations with interface: " + interface_id )

        #Get this interface relations
        query = self.db_operations.GET_NEIGHBOUR_SWITCH_RELATIONS_BY_INTERFACE
        args = (interface_id)
        results = self.db_operations.db_select_operation(query, args)

        for result in results:#Has just one
            remote_phys_address = result["physaddress"]
            remote_if_name = result["remoteinterfacename"]
        #print(str(remote_phys_address))
        #print(str(remote_if_name))

        # Get all switchs and find matching phys_address;
        query = self.db_operations.GET_ALL_SWITCHES_BY_PHYS_ADDRESS
        args = (remote_phys_address.replace(":", ""))
        switches = self.db_operations.db_select_operation(query, args)

        for result in switches:#Has just one
            remote_switch_identifier = result["identifier"]

        query = self.db_operations.GET_INTERFACE_BY_NAME_SWITCH
        args = (remote_if_name,remote_switch_identifier)
        interfacesb = self.db_operations.db_select_operation(query, args)
		
        for result in interfaces:  # Has just one
            remote_interfaces_id = ''.join(chr(i) for i in result[0])
		
        operations = []

        query = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID
        queryargs = query.format(interface_id)
        operations.append(queryargs)

        query = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID
        queryargs2 = query.format(remote_interfaces_id)
        operations.append(queryargs2)

        self.db_operations.db_insert_operations(operations)

        self.convergance()

    def convergance(self):
        self.log("Convergence request received.")
        Routing.convergance(self.db_operations)


    def log(self,data):
        Utils.cliLogger("[DataHandler] "+ data,0)









