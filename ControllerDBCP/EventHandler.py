import time
from threading import Thread
from Queue import Queue
from ControllerDBCP.DBoperations import DBoperations
from ControllerDBCP.DataHandler import Handler
from .Utils import Utils

import cps_object
import cps
import json
import subprocess

class NetworkMonitor:

    SLEEP_DURATION = 10

    def __init__(self, queue):
        self.q = queue
        self.db_operations = DBoperations()

    def log(self,data):
        Utils.cliLogger("[Statistics Event] "+ data,0)

    def statistics_monitor(self):
        self.log("Started Network Statistics Monitor...")
        while True:
            self.check_statistics()
            time.sleep(self.SLEEP_DURATION)
			
    def check_statistics(self):
        q.put((dh.update_statistics, (), {}))

class DBMonitor:

    INTERFACES_OPERATION_STATUS = "operstatus"
    SLEEP_DURATION = 0.1

    def __init__(self, queue):
        self.q = queue
        self.db_operations = DBoperations()
        self.clean_all_interface_log()
        self.clean_all_interface_neighbour_log()

    def changes_monitor(self):
        self.log("Started monitoring database changes...")
        while True:

            self.check_interfaces()
            self.check_interfaces_neighbour()
            time.sleep(self.SLEEP_DURATION)


    def check_interfaces(self):
        query = self.db_operations.GET_INTERFACES_CHANGES
        rows = self.db_operations.db_select_operation(query, '')
        if rows:
            Utils.timeLogger("---------------New Event---------------")
            Utils.timeLogger("EventHandler| Detected Event Interface Change: ")
        for row in rows:
            log_id = row["id"]
            interface_id = row["interfaceidentifier"].encode("ascii","ignore")
            update_type = row["updatetype"].encode("ascii","ignore")

            if update_type == self.INTERFACES_OPERATION_STATUS:
                self.change_operation_status_interface(interface_id)

            self.clean_interface_log(log_id)


    def check_interfaces_neighbour(self):
        query = self.db_operations.GET_INTERFACES_NEIGHBOUR_CHANGES
        rows = self.db_operations.db_select_operation(query, '')
        if rows:
            Utils.timeLogger("---------------New Event---------------")
            Utils.timeLogger("EventHandler| Detected Event Interface Neighbour Change: ")
            self.change_interface_neighbour()
            self.clean_all_interface_neighbour_log()

   
    def clean_interface_log(self,log_id):

        operations = []
        query = self.db_operations.DELETE_INTERFACE_LOG_BY_ID
        queryargs = query.format(log_id)
        operations.append(queryargs)
        self.db_operations.db_insert_operations(operations)

    def clean_interface_neighbour_log(self,log_id):

        operations = []
        query = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_LOG_BY_ID
        queryargs = query.format(log_id)
        operations.append(queryargs)
        self.db_operations.db_insert_operations(operations)

    def clean_all_interface_log(self,):

        operations = []
        query = self.db_operations.DELETE_INTERFACE_LOG
        operations.append(query)
        self.db_operations.db_insert_operations(operations)

    def clean_all_interface_neighbour_log(self,):

        operations = []
        query = self.db_operations.DELETE_INTERFACE_NEIGHBOUR_LOG
        operations.append(query)
        self.db_operations.db_insert_operations(operations)

    def change_operation_status_interface(self, interface_id):
        q.put((dh.interface_oper_status_change, (interface_id,), {}))
        self.log("Interface operation state changed: "+interface_id )

    def change_interface_neighbour(self,):
        q.put((dh.interface_neighbour_change, (), {}))
        self.log("Neighbour relationship changed!")

    def log(self, data):
        Utils.cliLogger("[DBmonitor] " + data, 0)

q = Queue()
dh = Handler()

net_monitor = NetworkMonitor(q)
thrd = Thread(target=net_monitor.statistics_monitor, args=())
thrd.start()

db_monitor = DBMonitor(q)
thrd = Thread(target=db_monitor.changes_monitor, args=())
thrd.start()

while True:
    f, args, kwargs = q.get()
    f(*args, **kwargs)
    q.task_done()
