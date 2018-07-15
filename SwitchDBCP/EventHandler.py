import time

from threading import Thread
from Queue import Queue
from SwitchDBCP.DBoperations import DBoperations
from SwitchDBCP.DataHandler import Handler
from SwitchDBCP.Interface import Interface
from .Utils import Utils

import cps_object
import cps
import json
import subprocess

LLDP_TXHOLD = "3"
LLDP_TXINTERVAL = "1"

class DBMonitor:
    IPV4_INSERT = "insert"
    IPV4_DELETE = "delete"
    IPV4_UPDATE = "update"
	
    SLEEP_DURATION = 0.05
    def __init__(self, queue):
        self.q = queue
        self.db_operations = DBoperations()

    def changes_monitor(self):
        self.log("Started monitoring database changes...")
        while True:

            self.check_ipv4rib()

            time.sleep(self.SLEEP_DURATION)

    def check_ipv4rib(self):

        query = self.db_operations.GET_ROUTE_DATA_LOG
        json = self.db_operations.db_select_operation(query, '')
		
        for item in json:
            log_id = int(item["id"])
            identifier =  item["identifier"].encode("ascii","ignore")
            operation =  item["operation"].encode("ascii","ignore")
            test = item["routeprefix"]
            if isinstance(test,unicode):
				log_route_prefix =  test.encode("ascii","ignore")
            else:
			    log_route_prefix =  ''.join(chr(i) for i in test)
            log_prefix_len = int(item["prefixlen"])
            switchidentifierfk = ''.join(chr(i) for i in item["switchidentifierfk"])

            if operation == self.IPV4_INSERT:
                self.insert_route(identifier)

            #(Extra Code)Added identifier to solve full replication problems
            elif operation == self.IPV4_DELETE:
                self.delete_route(switchidentifierfk,log_route_prefix, log_prefix_len)

            elif operation == self.IPV4_UPDATE:
                # It is assumed that an update does not change the route_prefix and prefix_len
                self.update_route(identifier, log_route_prefix, log_prefix_len)

            operations = []
            query = self.db_operations.DELETE_ROUTE_LOG
            queryargs = query.format(log_id)
            operations.append(queryargs)
            self.db_operations.db_insert_operations(operations)


    def insert_route(self,identifier):
        query = self.db_operations.GET_ROUTE_DATA
        args = (identifier)
        nrows = self.db_operations.db_select_operation(query, args)
        if not nrows:
            return
        else:            
            #(Extra code)This if is added to solve the problem of full replication
            ownid = dh.get_switch_by_physaddres()
            switchidentifierfk = ''.join(chr(i) for i in nrows[0]["switchidentifierfk"])
            if (switchidentifierfk == ownid):
                route_prefix = ''.join(chr(i) for i in nrows[0]["routeprefix"])
                prefix_len = nrows[0]["prefixlen"]
                weight = nrows[0]["weight"]
                if_name = ''
                next_hop = ''.join(chr(i) for i in nrows[0]["nexthop"])
                q.put((dh.add_route, (route_prefix, prefix_len, if_name, weight,next_hop), {}))
                self.log("New route: route prefix: " + str(route_prefix) + " prefix length: " + str(prefix_len) + " weight: " + str(weight) + " next-hop: " + str(next_hop))


    def delete_route(self,switchidentifierfk,log_route_prefix,log_prefix_len):
            #Extra code added to fix full replication
            ownid = dh.get_switch_by_physaddres()
            #print("Ownid: ",ownid)
            #print("Switchident: ",switchidentifierfk)
            #print(switchidentifierfk == ownid)
            if (switchidentifierfk == ownid):
                q.put((dh.del_route, (log_route_prefix, log_prefix_len), {}))
                self.log("Delete route: route prefix: " + log_route_prefix + " prefix length: " + str(log_prefix_len))


    def update_route(self,identifier, log_route_prefix, log_prefix_len):
        query = self.db_operations.GET_ROUTE_DATA
        args = (identifier)
        nrows = self.db_operations.db_select_operation(query, args)
        if not nrows:
            return
        else:
            #(Extra code)This if is added to solve the problem of full replication
            ownid = dh.get_switch_by_physaddres()
            switchidentifierfk = ''.join(chr(i) for i in nrows[0]["switchidentifierfk"])
            if (switchidentifierfk == ownid):
                route_prefix = ''.join(chr(i) for i in nrows[0]["routeprefix"])
                prefix_len = nrows[0]["prefixlen"]
                weight = nrows[0]["weight"]
                if_name = ''
                next_hop = ''.join(chr(i) for i in nrows[0]["nexthop"])
                q.put((dh.update_route, (route_prefix, prefix_len, if_name, weight,next_hop), {}))
                self.log("Updated route: route prefix: " + log_route_prefix + " prefix length: " + str(log_prefix_len))

    def log(self, data):
        Utils.cliLogger("[DBmonitor] " + data, 0)

class LLDPEvent:

    NEIGHBOUR_UPDATE = "lldp-updated"
    NEIGHBOUR_DELETE = "lldp-deleted"
    NEIGHBOUR_ADDED = "lldp-added"

    def __init__(self, queue):
        self.q = queue
    # Execute a command and return the output as a generator
    def run_command(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        while True:
            line = process.stdout.readline().rstrip()
            if not line:
                break
            yield line

    def lldp_watch_extractor(self):
        self.log("Configuring the LLDP protocol and starting neighbourhood listener...")
        counter = 0
        metadata = ""

        #Configuring LLDP
        subprocess.Popen(["sudo", "lldpcli","configure", "lldp", "tx-hold", LLDP_TXHOLD])
        subprocess.Popen(["sudo", "lldpcli", "configure", "lldp", "tx-interval", LLDP_TXINTERVAL])

        # Execute command and iterate over generator
        for output in self.run_command("lldpcli watch -f json"):
            # Get the complete json by parsing {}
            if '{' in output:
                counter += 1
            elif '}' in output:
                counter -= 1
            metadata = metadata + output

            # json is complete
            if counter == 0:

                data = json.loads(metadata)
                metadata = ""

                # Get operation
                lldp_operation = data.keys()[0]

                interface = data[lldp_operation]["interface"]

                if_name = interface.keys()[0]
                chassis_name = interface[if_name]["chassis"].keys()[0]

                if chassis_name != "id":  # Ignore id

                    age = interface[if_name]["age"]
                    mgmt_ip = interface[if_name]["chassis"][chassis_name]["mgmt-ip"][0]
                    remote_chassis_mac = interface[if_name]["chassis"][chassis_name]["id"]["value"]
                    remote_if_name = interface[if_name]["port"]["id"]["value"]
                    Utils.cliLogger("Interface name: " + if_name,1)
                    Utils.cliLogger("    Origin interface: " + remote_if_name,1)
                    Utils.cliLogger("    Origin chassis MAC: " + remote_chassis_mac,1)
                    Utils.cliLogger("    Age: " + age,1)
                    Utils.cliLogger("    Chassis name: " + chassis_name,1)
                    Utils.cliLogger("    Managment IP :" + mgmt_ip,1)
                    if lldp_operation == self.NEIGHBOUR_UPDATE:
                        pass
                        #q.put((dh.update_neighbour, (if_name, origin_mac,), {}))
                        #self.log("update: Interface: " + if_name + " from: "+ origin_mac + " with managment ip: "+mgmt_ip)
                    elif lldp_operation == self.NEIGHBOUR_DELETE:
                        q.put((dh.del_neighbour, (if_name,), {}))
                        #self.log("Delete: Interface: " + if_name """+ " from: " + remote_chassis_mac""")
                    elif lldp_operation == self.NEIGHBOUR_ADDED:
                        q.put((dh.add_neighbour, (if_name, remote_chassis_mac,remote_if_name), {}))
                        #self.log("Create: Interface: " + if_name + """" from: " + remote_chassis_mac +""" " with managment ip: " + mgmt_ip)
    def log(self,data):
        Utils.cliLogger("[Neighbourhood] "+ data,0)

# Work thread.
class CPSEvent:
    def __init__(self, queue):
        self.q = queue

    def monitor_events(self):
        self.log("Started CPS events listener...")
        interfaces_key = cps.key_from_name('observed', 'dell-base-if-cmn/if/interfaces-state/interface')

        handle = cps.event_connect()
        cps.event_register(handle, interfaces_key)

        while True:
            o = cps.event_wait(handle)
            obj = cps_object.CPSObject(obj=o)

            # Monitor interfaces
            if interfaces_key == obj.get_key():

                list = []
                cps.get([cps.key_from_name('observed', 'dell-base-if-cmn/if/interfaces-state/interface')], list)
                # Ignore the first entry
                for entry in list[1:]:
                    # Construct a new object for each entry
                    get_obj = cps_object.CPSObject(obj=entry)
                    if ( obj.get_attr_data("if/interfaces-state/interface/name")== get_obj.get_attr_data("if/interfaces-state/interface/name")):

                        oper_status = get_obj.get_attr_data("if/interfaces-state/interface/oper-status")
                        # ...

                        new_list = []
                        cps.get([cps.key_from_name('target', 'dell-base-if-cmn/if/interfaces/interface')], new_list)

                        # Ignore the first entry
                        for aux_entry in new_list[1:]:
                            # Construct a new object for each entry
                            get_aux_obj = cps_object.CPSObject(obj=aux_entry)

                            if (get_aux_obj.get_attr_data("if/interfaces/interface/name") == obj.get_attr_data("if/interfaces-state/interface/name")):
                                if_name = get_aux_obj.get_attr_data("if/interfaces/interface/name")
                                #enabled = get_aux_obj.get_attr_data("if/interfaces/interface/enabled")
                                Utils.cliLogger(if_name, 1)
                                Utils.cliLogger(0, 1)
                                interface = Interface(if_name, "", 0, "", "", oper_status, "","","")
                                q.put((dh.change_interface, (interface,), {}))
                                #self.log("Operstatus changed: " + str(oper_status) + " Interface: " + if_name)

    def log(self,data):
        Utils.cliLogger("[CPS Event] "+ data,0)


q = Queue()
dh = Handler()

lldp_exctractor = LLDPEvent(q)
thrd = Thread(target=lldp_exctractor.lldp_watch_extractor, args=())
thrd.start()

cps_event = CPSEvent(q)
thrd = Thread(target=cps_event.monitor_events, args=())
thrd.start()

db_monitor = DBMonitor(q)
thrd = Thread(target=db_monitor.changes_monitor, args=())
thrd.start()

while True:
    f, args, kwargs = q.get()
    f(*args, **kwargs)
    q.task_done()