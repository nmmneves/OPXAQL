import requests

class DBoperations:
    def db_insert_operations(self, querylist):
        for query in querylist:
            #print("Query: ",query)
            r = requests.post('http://localhost:3002/aql', data={'query':query})
            if(r.status_code != 200):
                print("Something went wrong in:",query,r.reason)

    def db_select_operation(self, operation, args):
        if args:
            opwithargs = operation.format(args)
            #print("Query: ",opwithargs)
            r = requests.post('http://localhost:3002/aql', data={'query': opwithargs})
        else:
            r = requests.post('http://localhost:3002/aql', data={'query': operation})
            #print(operation)
        if(r.status_code != 200):
            print("Something went wrong",operation,r.reason)
        result = r.json()[0]
        return result

    # QUERYS

    INSERT_NEIGHBOUR =  "INSERT INTO neighbours(physaddress,switchidentifierfk) VALUES (\'{}\',\'{}\')"

    INSERT_INTERFACE_NEIGHBOUR = "INSERT INTO interfaceneighbour(interfaceid,physaddress,remoteinterfacename,switchidentifierfk)" \
                     " VALUES (\'{}\',\'{}\',\'{}\',\'{}\')"

    INSERT_SWITCH = "INSERT INTO switch(identifier,name,physaddress,managementip) VALUES (\'{}\',\'{}\',\'{}\',\'{}\')"

    INSERT_INTERFACE = "INSERT INTO interfaces(identifier,name,type,enabled,operstatus,physaddress,speed,mtu,switchidentifierfk,ip,prefixlength) "\
	                   "VALUES (\'{}\',\'{}\',\'{}\',{},{},\'{}\',\'{}\',{},\'{}\',\'{}\',{})"

    INSERT_INTERFACE_UNUSED = "INSERT INTO interfaces(identifier,name,type,enabled,operstatus,physaddress,speed,mtu,switchidentifierfk,ip) "\
	                          "VALUES (\'{}\',\'{}\',\'{}\',{},{},\'{}\',\'{}\',{},\'{}\',\'{}\')"
					   
    DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID = "DELETE FROM interfaceneighbour WHERE interfaceid = \'{}\'"

    DELETE_ROUTE_LOG = "DELETE FROM ipvfourribchangeslog WHERE id = {}"

    DELETE_INTERFACE_LOG = "DELETE FROM interfaceschangeslog WHERE id = {}"
		
    GET_IDENTIFIER_FROM_NAME = "SELECT identifier,switchidentifierfk FROM interfaces WHERE name = \'{}\'"

    GET_IDENTIFIER_FROM_SWITCH = "SELECT identifier FROM switch"

    GET_NEIGHBOUR_COUNT_FROM_PHYSADDRESS = "SELECT * FROM neighbours WHERE physaddress = \'{}\'"
	
    GET_ROUTE_DATA_LOG = "SELECT * FROM ipvfourribchangeslog"

    GET_ROUTE_DATA = "SELECT routeprefix,prefixlen,weight,nexthop,switchidentifierfk FROM ipvfourrib WHERE identifier = \'{}\' "
	
    GET_INTERFACE_DATA_LOG = "SELECT id, interfaceidentifier,updatetype FROM interfaceschangeslog"

    GET_INTERFACE_FROM_IDENTIFIER = "SELECT name,enabled FROM interfaces WHERE identifier = \'{}\'"

    GET_IP_FROM_INTERFACE = "SELECT name,ip,prefixlength FROM interfaces WHERE identifier = \'{}\'"
	
    UPDATE_INTERFACE_OPERSTATUS = "UPDATE interfaces SET operstatus ASSIGN {} WHERE identifier = \'{}\'"
     
	#GET_NEIGHBOUR_COUNT_FROM_PHYSADDRESS = "select count(*) from `neighbours` where `phys-address` = %s"
	#(Extra code) To deal with full replication
	
    GET_IDENTIFIER_FROM_SWITCH_BY_PHYSADDRESS = "SELECT identifier FROM switch WHERE physaddress = \'{}\'"
	
    GET_IDENTIFIER_FROM_NAME_AND_SWITCH = "SELECT identifier,switchidentifierfk FROM interfaces WHERE name = \'{}\'  AND  switchidentifierfk = \'{}\'"

    #Used for statistics monitor
	
    GET_INTERFACE_NAMES = "SELECT name FROM interfaces WHERE switchidentifierfk = \'{}\'"
	
    GET_STATISTICS = "SELECT packetsinhundredseconds,packetsouthundredseconds FROM networkstatistics WHERE switchidentifierfk = \'{}\'"

    INSERT_STATISTICS = "INSERT INTO networkstatistics (switchidentifierfk,hour,counter,packetsintensecond,packetsinhundredseconds,packetsouttensecond,packetsouthundredseconds) VALUES (\'{}\',{},{},{},{},{},{})"