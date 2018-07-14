import requests

class DBoperations:
    def db_insert_operations(self, querylist):
        for query in querylist:
            #print(query)
            r = requests.post('http://localhost:3002/aql', data={'query':query})
            if(r.status_code != 200):
                print("Something went wrong in:",query,r.reason)

    def db_select_operation(self, operation, args):
        if args:
            opwithargs = operation.format(args)
            #print(opwithargs)
            r = requests.post('http://localhost:3002/aql', data={'query': opwithargs})
        else:
            r = requests.post('http://localhost:3002/aql', data={'query': operation})
            #print(operation)
        if(r.status_code != 200):
            print("Something went wrong",operation,r.reason)
        result = r.json()[0]
        return result
	
	#QUERYS
	
    #GET_ALL_NEIGHBOUR_SWITCH_RELATIONS = "select `interface_neighbour`.`switch_identifier_fk`,`interface_neighbour`.`phys-address`,interfaces.name  from `interface_neighbour` inner join interfaces on interfaces.identifier = `interface_neighbour`.`interface_id`"
    GET_ALL_INTERFACE_NEIGHBOUR = "SELECT interfaceid,switchidentifierfk,physaddress FROM interfaceneighbour"
    GET_ALL_NEIGHBOUR_SWITCH_RELATIONS_INTERFACE = "SELECT name,identifier FROM interfaces"

    #GET_NUMBERED_INTERFACES = "SELECT `ip`,`prefix-length`,`switch_identifier_fk`,`name`,`oper-status` FROM `interfaces` WHERE  `ip`!=''"
    GET_NUMBERED_INTERFACES = "SELECT ip,prefixlength,switchidentifierfk,name,operstatus FROM interfaces WHERE ip <> ''"

	#GET_ALL_SWITCHES = "SELECT `identifier`, `phys-address` FROM `switch`"
    GET_ALL_SWITCHES = "SELECT identifier,physaddress FROM switch"

	#GET_ALL_SWITCHES_BY_PHYS_ADDRESS = "SELECT `identifier` FROM `switch` where `phys-address` = %s"
    GET_ALL_SWITCHES_BY_PHYS_ADDRESS = "SELECT identifier FROM switch WHERE physaddress = \'{}\' "

	#GET_ALL_CURRENT_ROUTES = "SELECT `route-prefix`,`prefix-len`,weight,`next-hop`,`switch_identifier_fk`,`identifier` FROM `ipvfourrib`"
    GET_ALL_CURRENT_ROUTES = "SELECT routeprefix,prefixlen,weight,nexthop,switchidentifierfk,identifier FROM ipvfourrib"

    #GET_NEIGHBOUR_SWITCH_RELATIONS_BY_INTERFACE = "select `phys-address`,`remote_interface_name` from `interface_neighbour` where `interface_id` = %s"
    GET_NEIGHBOUR_SWITCH_RELATIONS_BY_INTERFACE = "SELECT physaddress,remoteinterfacename FROM interfaceneighbour WHERE interfaceid = \'{}\' "

    #GET_INTERFACE_BY_NAME_SWITCH = "SELECT `identifier` FROM `interfaces` WHERE  `name` = %s and `switch_identifier_fk` = %s"
    GET_INTERFACE_BY_NAME_AND_ID = "SELECT identifier FROM interfaces WHERE  name = \'{}\' AND switchidentifierfk = \'{}\' "
	
	#GET_INTERFACE_OPER_STATUS_BY_NAME_ID = "SELECT `oper-status` FROM `interfaces` WHERE  `identifier` = %s"
    GET_INTERFACE_OPER_STATUS_BY_NAME_ID = "SELECT operstatus FROM interfaces WHERE identifier = \'{}\'"

	#GET_INTERFACES_CHANGES = """SELECT id,`interface-identifier`, `update-type` FROM `interfaces-changes-log`"""
    GET_INTERFACES_CHANGES = "SELECT id,interfaceidentifier,updatetype FROM interfaceschangeslog"

	#GET_INTERFACES_NEIGHBOUR_CHANGES = """SELECT id,`interface-identifier` FROM `interface_neighbour-changes-log`"""
    GET_INTERFACES_NEIGHBOUR_CHANGES = "SELECT id,interfaceidentifier FROM interfaceneighbourchangeslog"
	
	#INSERT_NEW_ROUTE = """insert into `ipvfourrib`(identifier,`route-prefix`,`prefix-len`,`next-hop`,weight, `switch_identifier_fk`)  values(%s,%s,%s,%s,%s,%s)"""
    INSERT_NEW_ROUTE = "INSERT INTO ipvfourrib (identifier,routeprefix,prefixlen,nexthop,weight,switchidentifierfk) VALUES (\'{}\',\'{}\',{},\'{}\',{},\'{}\')"
		
    #DELETE_ROUTE_BY_IDENTIFIER = """delete FROM `ipvfourrib` where identifier = %s"""
    DELELE_ROUTE_BY_IDENTIFIER = "DELETE FROM ipvfourrib WHERE identifier = \'{}\'"

	#DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID = "delete from `interface_neighbour` where `interface_id` = %s"
    DELETE_INTERFACE_NEIGHBOUR_BY_INTERFACEID = "DELETE FROM interfaceneighbour WHERE interfaceid = \'{}\'"

    #DELETE_INTERFACE_LOG_BY_ID = """delete FROM `interfaces-changes-log` where id = %s"""
    DELETE_INTERFACE_LOG_BY_ID = "DELETE FROM interfaceschangeslog WHERE id = \'{}\'"

    #DELETE_INTERFACE_NEIGHBOUR_LOG_BY_ID = """delete FROM `interface_neighbour-changes-log` where id = %s"""
    DELETE_INTERFACE_NEIGHBOUR_LOG_BY_ID = "DELETE FROM interfaceneighbourchangeslog WHERE id = \'{}\'"

    #DELETE_INTERFACE_LOG = """delete FROM `interfaces-changes-log`"""
    DELETE_INTERFACE_LOG = "DELETE FROM interfaceschangeslog"

    #DELETE_INTERFACE_NEIGHBOUR_LOG = """delete FROM `interface_neighbour-changes-log`"""
    DELETE_INTERFACE_NEIGHBOUR_LOG = "DELETE FROM interfaceneighbourchangeslog"

"""    Extra code to deal with full replication
    DELETE_ALL_ROUTES = "DELETE FROM ipvfourrib"

import mysql.connector

DATABASE_ACCESS_DATA_FILE = "Controller/database_config.txt"
class DBoperations:
    def __init__(self):

        file = open(DATABASE_ACCESS_DATA_FILE, "r")
        content = file.read().splitlines()
        self.dbconfig = {
            "user": str(content[0]),
            "password": str(content[1]),
            "host": str(content[2]),
            "database": str(content[3])
        }
        file.close()

        mysql.connector.connect(pool_name="mypool", pool_size=32, **self.dbconfig)

    def db_insert_operations(self, oper_list):
        cnx = mysql.connector.connect(pool_name="mypool")
        try:
            cursor = cnx.cursor()
            for operation in oper_list:
                cursor.execute(operation[0], operation[1])
            cnx.commit()
        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))

        finally:
            cursor.close()
            cnx.close()

    def db_select_operation(self, operation, args):
        cnx = mysql.connector.connect(pool_name="mypool")
        try:
            cursor = cnx.cursor()
            cursor.execute(operation, args)
            result = cursor.fetchall()

        except mysql.connector.Error as err:
            print("Something went wrong: {}".format(err))
        finally:
            cursor.close()
            cnx.close()
            return result
"""