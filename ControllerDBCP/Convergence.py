from ControllerDBCP.DBoperations import DBoperations
import networkx as nx
import copy
from ControllerDBCP.Route import Route
from .Utils import Utils
import uuid
import time

#To see what the algorithm is doing uncomment all prints and related code.
#This code was written in a readable way.
#It can clearly be improved by removing redundant cycles and improve algorithm time complexity

class Routing:

    @staticmethod
    def getNextHopIP(router_id, next_hop_list, neigb_relations_results, interfaces,
                          switch_identifier_by_phy_address):
#-------------Get the IP address of the interface that relates to this router and is listed on the next-hop list

        exit_IP_array = []
        
        for next_hop in next_hop_list:
            for result in neigb_relations_results:
                switch_identifier_local = ''.join(chr(i) for i in result["switchidentifierfk"])
                if (switch_identifier_local == next_hop):
                    if_name_local = result["name"]
                    phystemp = ''.join(chr(i) for i in result["physaddress"])
                    switch_identifier_remote = switch_identifier_by_phy_address.get(str(phystemp).replace(":",""))
                    if(switch_identifier_remote==router_id):
                        # Get the interface IP address!
                        for result in interfaces:
                            ip =  ''.join(chr(i) for i in result["ip"])
                            switch_id = ''.join(chr(i) for i in result["switchidentifierfk"])
                            if_name = ''.join(chr(i) for i in result["name"])
                            if (if_name_local == if_name and switch_id == next_hop):
                                exit_IP_array.extend([str(ip)])

        return exit_IP_array

    @staticmethod
    def getUpdatedGlobalRoutingRules(db_operations):

        #######1 ---  Start by obtaining all the reachable networks.

        #Only 8,16,24 and 32 networks

        #Query database and extract all interfaces IP addresses and prefixes

        query = db_operations.GET_NUMBERED_INTERFACES
        interfaces = db_operations.db_select_operation(query,'')

        networks_dict = dict()

#----------------Get all networks from all interfaces (Up or down). Then remove those that have at least one interfaces down that reaches that network.
#-----------------This imposition com from  having point-to-point connection
        for result in interfaces:
            ip = ''.join(chr(i) for i in result["ip"])
            prefix_lenght = result["prefixlength"]
            switch_id = ''.join(chr(i) for i in result["switchidentifierfk"])
            oper_status = result["operstatus"]
            #print("Going with IP: "+ str(ip) +"/"+str(prefix_lenght))
            #Get network from the IP and predix
            network = Utils.extractNetworkFromIpv4(ip,prefix_lenght)
            #Create a dictionary with all networks and associated switches
            #print("Network: " + network)
            if (network not in networks_dict):
                if(oper_status==1):
                    networks_dict[network] = [switch_id,]
                    #print("oper_status = 1: " + network)
                else:
                    #print("oper_status != 1: " + network)
                    networks_dict[network] = [None, ]
            else:

                switch_list = networks_dict[network]
                if (oper_status == 1):#(Only operational interfaces i.e oper-status = 1)
                    #print("oper_status = 1: " + network)
                    #If switch not associated with the network, then do it
                    if(switch_id not in switch_list):
                        switch_list.extend([switch_id])
                        networks_dict[network] = switch_list
                else:
                    #print("oper_status != 1: " + network)
                    switch_list.extend([None])
                    networks_dict[network] = switch_list

        #for i in networks_dict:
            #print (i, networks_dict[i])

        #Remove networks not considered
        dummy_networks_dict = copy.deepcopy(networks_dict)
        for dummy_network in dummy_networks_dict:
            #print("dummy:"+str(dummy_networks_dict[dummy_network]))
            for switch in dummy_networks_dict[dummy_network]:
                if (switch is None):
                    #print("-------"+str(dummy_network))
                    del networks_dict[dummy_network]

        #print("-----All discovered reachable networks and by which switches------")
        #for i in networks_dict:
        #    print(i, networks_dict[i])

        #print("")
        #print("")
        #print("")

        #OK

        ##Elect all candidate switches that reach a network, an individual view
        query = db_operations.GET_ALL_SWITCHES
        switches = db_operations.db_select_operation(query,'')

        router_network_destination_view_dic = dict()

        #print("-----Switch view of reachable networks by which switch---------")

        #for every switch on the network
        for switch in switches:
            switch_identifier = ''.join(chr(i) for i in switch["identifier"])
            single_router_network_destination_view_dic = copy.deepcopy(networks_dict)

            #Start with electing the switches that candidate for last last hop before reaching the network
            #Check every network
            for network in single_router_network_destination_view_dic:
                #Check if the current router connects to the network.
                if (switch_identifier in single_router_network_destination_view_dic[network]):
                    #We have a direct connection to the network via the current switch, delete the rest
                    single_router_network_destination_view_dic[network] = [switch_identifier, ]
                #Maintain the rest

            router_network_destination_view_dic[switch_identifier] = single_router_network_destination_view_dic


            #print("switch: " + switch_identifier + "")
            #for i in single_router_network_destination_view_dic:
                #print(i, single_router_network_destination_view_dic[i])
        #print("")
        #print("")
        #print("")


                #OK

#################################################4
        #Create a graph of the network
        #print("----Paths created between nodes-----")
        G = nx.DiGraph()

        #Get all switches on the network and their chassis MAC address
        #reuse query
        nodes_results = switches

        i = 0
        switch_identifier_by_phy_address = {}

        #Create a node for every switch
        for result in nodes_results:
            i += 1;
            identifier = ''.join(chr(i) for i in result["identifier"])
            phys_address = ''.join(chr(i) for i in result["physaddress"])
            #self.log("Node " + str(i) + ": " + identifier + " " + phys_address)
            switch_identifier_by_phy_address[phys_address] = identifier
            G.add_node(identifier, id=identifier)

        #---------------------------------------------------------------------------------------Get all neighbour relationships with reference to the interfaces-----------------------	
        query = db_operations.GET_ALL_NEIGHBOUR_SWITCH_RELATIONS_INTERFACE
        identifiernames = db_operations.db_select_operation(query,'')		

        query2 = db_operations.GET_ALL_INTERFACE_NEIGHBOUR
        interneighbours = db_operations.db_select_operation(query2,'')

        for neighbour in interneighbours:
            interid = ''.join(chr(i) for i in neighbour["interfaceid"])
            for idname in identifiernames: 
                identifier = ''.join(chr(i) for i in idname["identifier"])
                if(interid == identifier):
                    neighbour["name"] = ''.join(chr(i) for i in idname["name"])
        neigb_relations_results = interneighbours
        #---------------------------------------------------------------------------------------Get all neighbour relationships with reference to the interfaces-----------------------	
        #create edges among nodes
        for result in neigb_relations_results:
            switch_identifier_local = ''.join(chr(i) for i in result["switchidentifierfk"])
            phys_address = ''.join(chr(i) for i in result["physaddress"])
            if_name_local = result["name"]
            tempstring = str(''.join(chr(i) for i in result["physaddress"])).replace(":", "")
            switch_identifier_remote = switch_identifier_by_phy_address.get(tempstring)
            #print("" + switch_identifier_local + "-->" + switch_identifier_remote)
            G.add_edge(switch_identifier_local, switch_identifier_remote, name=if_name_local)
        #print("")
        #print("")
        #print("")
###################################5
        ##Calculate shortes path to every other router
        ##Can be improved in terms of efficiency

        #print("----Paths created by the shortest-path algorithm-----")
        paths_dict = dict()
        for orign in nodes_results:
            origin_id = ''.join(chr(i) for i in orign["identifier"])
            paths_dict[origin_id] = []
            for destination in nodes_results:
                destination_id = ''.join(chr(i) for i in destination["identifier"])

                try:
                    path = nx.shortest_path(G, source=origin_id, target=destination_id)

                    paths_dict[origin_id].extend([path])
                    #print(path)
                except:
                    Routing.log("Path from " + origin_id + " to " + destination_id + " failed or does not exist")


        #for i in paths_dict:
            #print("Origin: " + i + "")
            #listaa= paths_dict[i]
            #for a in listaa:
                #print(a)

        #print("")
        #print("")
        #print("")
################################6
        #Get next-hops by network for each router
        #print("----Get next-hops by network for each router-----")
        final_router_network_destination_view_dic = copy.deepcopy(router_network_destination_view_dic)
        for router_id in router_network_destination_view_dic:
            single_router_network_destination_view_dic = router_network_destination_view_dic[router_id]
            for network in single_router_network_destination_view_dic:
                # Need to find the next-hop to reach this network.
                # We now use the elected switches.
                # If we have one, that is the next-hop
                # If we have more than one we choose the one with shortest path
                # If equal path than keep all equal for now
                #print("-- Working now with switch "+ router_id + " and network " + network +" ---")
                candidate_router_list =  single_router_network_destination_view_dic[network]
                #Get path with least cost(steps)
                path_list = paths_dict[router_id]
                smallest_cost= -1
                candidate_smaller_cost = []
                for candidate in candidate_router_list:
                    #print("Trying candidate " + candidate)
                    # quantify the cost of this path
                    for path in path_list:
                        #if this path leads to candidate router
                        if(path[-1]==candidate):
                            cost=len(path)
                            #print("This candidate has cost " + str(cost))
                            if (smallest_cost==-1):
                                #print("Adding first cost candidate " + candidate)
                                smallest_cost=cost
                                candidate_smaller_cost.extend([candidate])
                            elif(smallest_cost>cost):
                                #print("Adding new cost candidate " + candidate)
                                smallest_cost=cost
                                candidate_smaller_cost= [candidate,]
                            elif (smallest_cost == cost):
                                #print("Adding equal cost candidate " + candidate)
                                candidate_smaller_cost.extend([candidate])
                #for candid in candidate_smaller_cost:
                    #print ("Selected lower cost candidate: "+  candid)

                #We have the shortest path cost so replace the candidates routers with next-hop switch identifiers
                #print("Finished cost, now get the path and next-hop that have that lowest cost")
                next_hop_list = []
                for path in path_list: #Cleary redundant
                    for candidate in candidate_smaller_cost:

                        if (path[-1] == candidate):
                            #print("Getting next-hop for destination switch: " + candidate)
                            if smallest_cost == 1:
                                next_hop_list.extend([path[0]])#Get the only host(local)
                            else:
                                #print("Path found for destinaiton: " + candidate + " with next-hop: "+ path[1])
                                next_hop_list.extend([path[1]])#Get the next
                final_router_network_destination_view_dic[router_id][network]=next_hop_list

        route_list=[]
        #print("-------------------------List after next hop calc------------------------------")
        #print(final_router_network_destination_view_dic)
        for router_id in final_router_network_destination_view_dic:
            for network in final_router_network_destination_view_dic[router_id]:
                next_hop_IP = Routing.getNextHopIP(router_id, final_router_network_destination_view_dic[router_id][network],
                                          neigb_relations_results, interfaces, switch_identifier_by_phy_address)

                for next_hop in next_hop_IP:
                    route = Route(router_id, network, prefix_lenght, next_hop, 100)
                    route_list.extend([route])
                    break#We might get multiple available next-hops, for now we accept just one (any)
        #print("End route list: ",route_list)
        return route_list

    @staticmethod
    def convergance(db_operations):
        Utils.timeLogger("Convergence| Convergence Started: ")
        Routing.log("Convergence started...")
        
        route_list = Routing.getUpdatedGlobalRoutingRules(db_operations)

        # We need to evaluate the currant database state and
        # compare the new routes with the routes on the database:
        # --New route, not present on the database, must be inserted.
        # --Already present routes on the database are ignored
        # --Routes present on the database but not on the new route list must be deleted.
        Utils.timeLogger("Convergence| Convergence Finished: ")
        query = db_operations.GET_ALL_CURRENT_ROUTES
        db_route_list = db_operations.db_select_operation(query,'')
        #print(db_route_list)
        # The route might not exist anymore
        operations = []
        for db_route in db_route_list:
            route_prefix = ''.join(chr(i) for i in db_route["routeprefix"])
            prefix_len = db_route["prefixlen"]
            next_hop =  ''.join(chr(i) for i in db_route["nexthop"])
            switch_identifier_fk =  ''.join(chr(i) for i in db_route["switchidentifierfk"])
            identifier =   ''.join(chr(i) for i in db_route["identifier"])
            #print("Switch id:",switch_identifier_fk)
            route_exists = False

            for route in route_list[:]:
                if (route.router_id==switch_identifier_fk
                        and route.network==route_prefix
                        and route.prefix_length==prefix_len
                        and route.next_hop==next_hop):
                    #Existes on the database and new routes ----> remove from the new route list.
                    route_exists=True
                    route_list.remove(route)
                    Routing.log("Route removed from the list: " + route_prefix + "-> " + next_hop + " " + route.router_id)
                    break

            if (route_exists==False):
                # Exists on the database but not on the new route list -----> delete from the database

                query = db_operations.DELELE_ROUTE_BY_IDENTIFIER
                queryargs = query.format(identifier)
                operations.append(queryargs)
                Routing.log("Route removed from the database: " + route_prefix + "-> "+next_hop)
        db_operations.db_insert_operations(operations)
        # Go on with the rest operations

        for route in route_list:
            Routing.log("Route to be insert on the database: " + route.network + "-> " + route.next_hop)
            query =  db_operations.INSERT_NEW_ROUTE
            queryargs = query.format(str(uuid.uuid4()), route.network, route.prefix_length,route.next_hop,route.metric, route.router_id)
            operations.append(queryargs)
            #print("Router id: ",route.router_id)
            db_operations.db_insert_operations(operations)
            operations = []
         

        Routing.log("Convergence finished. Updating database...")
        Utils.timeLogger("Convergence| Insertions and Deletions Done: ")
        Routing.log("Database update finished...")
		
    @staticmethod
    def log(data):
        Utils.cliLogger("[Convergence] " + data, 0)