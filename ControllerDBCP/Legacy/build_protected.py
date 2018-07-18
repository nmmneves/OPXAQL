from Controller.DBoperations import DBoperations
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

db_operations = DBoperations()
G=nx.DiGraph()

query = """select identifier, `phys-address` from switch """
args = ()
nodes_results = db_operations.db_select_operation(query, args)

i=0
dicts = {}
for result in nodes_results:
    i+=1;
    identifier=result[0]
    phys_address = result[1]
    print("Node " + str(i) +": " + identifier + " " + phys_address)
    dicts[phys_address] = identifier
    G.add_node(identifier,id=identifier)


query = """select `interface_neighbour`.`switch_identifier_fk`,`interface_neighbour`.`phys-address`,interfaces.name  from `interface_neighbour` inner join interfaces on interfaces.identifier= `interface_neighbour`.`interface_id`"""
args = ()
neigb_relations_results = db_operations.db_select_operation(query, args)

for result in neigb_relations_results:
    switch_identifier_local = result[0]
    phys_address = result[1]
    if_name_local =  result[2]
    switch_identifier_remote = dicts.get(str(result[1]).replace(":", ""))
    print(""+switch_identifier_local+"-->"+switch_identifier_remote)

    G.add_edge(switch_identifier_local, switch_identifier_remote,name = if_name_local )







plt.figure(figsize=(9,9))
plt.title('Network topology')
plt.axis('off')

pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=False)
for p in pos:  # raise text positions
    pos[p][1] += 0.05
nx.draw_networkx_labels(G, pos,font_size=6)

edge_labels=dict([((v,u,),d['name'])
             for u,v,d in G.edges(data=True)])
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.25, font_size=5)

plt.savefig("plot.pdf", dpi=1000)


#Draw all shortest paths


i=0;
for orign in nodes_results:
    origin_id=orign[0]
    for destination in nodes_results:
        i+=1
        destination_id = destination[0]
        path = nx.shortest_path(G,source=origin_id,target=destination_id)
        print(path)
        plt.axis('off')

        plt.figure(figsize=(9, 9))
        plt.title("" + origin_id + " ----> " + destination_id)
        nx.draw(G, pos, node_color='k',with_labels=False)


        path_edges = zip(path,path[1:])
        nx.draw_networkx_nodes(G,pos,nodelist=path,node_color='r')
        nx.draw_networkx_edges(G,pos,edgelist=path_edges,edge_color='r',width=2)

        for p in pos:  # raise text positions
            pos[p][1] += 0.05
        nx.draw_networkx_labels(G, pos, font_size=6)

        edge_labels = dict([((v, u,), d['name'])
                            for u, v, d in G.edges(data=True)])
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, label_pos=0.25, font_size=5)
        plt.savefig("path"+str(i)+".pdf", dpi=1000)














