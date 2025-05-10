import networkx as nx #used for creating, manipulating, and analyzing graphs
from networkx.algorithms.shortest_paths.generic import shortest_path
import matplotlib.pyplot as plt #used for visualization
from networkx.algorithms.simple_paths import all_simple_paths
from tabulate import tabulate #for flow table
import random

#SHA-256 hash: d1ac131feb230184c899a76beb5eafe302e0251a4da3842380947f5b7d5d2cb2

#Build graph object
class SDN_controller:

    #initialize empty directed graph
    def __init__(self):
        self.graph = nx.DiGraph()
        self.flow_table = {}

    #Add node to graph
    def add_node(self, node_id):
        self.graph.add_node(node_id)

    #Add directed edge
    def add_edge(self, src, dest):
        self.graph.add_edge(src, dest)

    #Print visual graph
    def graph_vis(self, flow = None):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True)
        if flow:
            path_edge = list(zip(flow, flow[1:]))
            nx.draw_networkx_edges(self.graph, pos, edgelist=path_edge, edge_color='red')
        plt.show()

    #Find the shortest path between nodes
    def shortest_path(self, src, dest):
        try:
            path = nx.shortest_path(self.graph, src, dest)
            return path
        #If no path print error
        except nx.NetworkXNoPath:
            print("No path available from {} to {}".format(src, dest))
            return None

    #Add entries for flow table
    def flow(self, src, dest, priority="normal"):
        try:
            #all paths
            paths = list(nx.all_shortest_paths(self.graph, src, dest))
            if not paths:
                return
            #load balance by choosing random path
            path = random.choice(paths)
            print(f"Current path from {src} to {dest}: {path}")
            #backup
            backup = None
            #backup for high priority
            if priority == "high":
                simple = list(nx.all_simple_paths(self.graph, src, dest, cutoff=10))
                candidate = [p for p in simple if p != path]
                if candidate:
                    backup = min(candidate, key=len)
                    print(f"Backup path from {src} to {dest}: {backup}")
                else:
                    print(f"No backup path available from {src} to {dest}")
            #navigates path from source to destination populating flow table
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node = path[i + 1]
                if current_node not in self.flow_table:
                    self.flow_table[current_node] = {}
                self.flow_table[current_node][dest] = next_node, priority, backup

        except nx.NetworkXNoPath:
            pass

    #for generating flow table using tabulate
    def print_flow(self):
        data = []
        headers = ["src", "dst", "next_node", "priority", "backup path"]
        for src, rules in self.flow_table.items():
            for dst, (next_node, priority, backup) in rules.items():
                data.append([src, dst, next_node, priority, backup if backup else "None"])
        print(tabulate(data, headers=headers, tablefmt="grid"))

    #Simulate link failure
    def link_fail(self, src, dest):
        if self.graph.has_edge(src, dest):
            self.graph.remove_edge(src, dest)
            del self.flow_table[src][dest]
            print("Link failed for {} to {}".format(src, dest))
            print("Rerouting link between {} and {}".format(src, dest))
            if self.shortest_path(src, dest) != None:
                print("New path from {} to {}".format(src, dest), self.shortest_path(src, dest))
                controller.flow(src, dest)
        else:
            print("No link between {} and {}".format(src, dest))

    #reconfigure path
    def fix_link(self, src, dest):
        if self.graph.has_edge(src, dest):
            print("Edge already exists for {} to {}".format(src, dest))
        else:
            self.graph.add_edge(src, dest)
            print("Edge created for {} to {}".format(src, dest))
            self.flow_table.clear()
            self.initialT()

    #Initialize existing topology into flow table
    def initialT (self):
        nodes = list(self.graph.nodes())
        for src in nodes:
            for dest in nodes:
                if src != dest:
                    self.flow(src, dest)

#Create topology using graph and print it
if __name__ == "__main__":
    controller = SDN_controller()
    #Add nodes
    controller.add_node("A")
    controller.add_node("B")
    controller.add_node("C")
    controller.add_node("D")
    #Add edges
    controller.add_edge("A", "B")
    controller.add_edge("A", "C")
    controller.add_edge("B", "C")
    controller.add_edge("B", "D")

    #Print current topology & visual
    print("Current Topology:")
    print("Nodes:", controller.graph.nodes())
    print("Edges:", controller.graph.edges())

    controller.initialT()
    print("Please choose one of the following:\n(1) Find the shortest path "
                       "between two nodes.\n(2) Print the flow table.\n(3) Simulate a link failure\n"
                       "(4) Fix/create link.\n(5) Print current topology.\n(6) Create a Topology diagram.\n(7) Print Commands."
                        "\n(8) Create new node.\n(9) Delete Node.\n(10) Exit.")

    #Getting source and destination nodes and returning shortest path/flow table
    while True:
        while True:
            user_input = input("Number: ")
            if user_input == "1" or user_input == "3" or user_input == "4":
                start_input = input("Enter the source node: ")
                if start_input in controller.graph.nodes:
                    start = start_input
                else:
                    print("Source node not found")
                    break
                finish_input = input("Enter the destination node: ")
                if finish_input in controller.graph.nodes:
                    finish = finish_input
                else:
                    print("Destination node not found")
                    break
                if user_input == "1":
                    priority = input("Please enter priority (low, normal, high): ")
                    if priority not in ["high", "normal", "low"]:
                        print("Invalid priority: set as normal")
                        priority = "normal"
                    controller.flow(start, finish, priority=priority)
                    break
                if user_input == "3":
                    controller.link_fail(start, finish)
                    break
                if user_input == "4":
                    controller.fix_link(start, finish)
                    break
            if user_input == "2":
                controller.print_flow()
                break
            if user_input == "6":
                controller.graph_vis()
                print("Topology Diagram created.")
                break
            if user_input == "5":
                print("Current Topology:")
                print("Nodes:", controller.graph.nodes())
                print("Edges:", controller.graph.edges())
                break
            if user_input == "8":
                node = input("Enter new node: ")
                if node in controller.graph.nodes:
                    print("Node already exists for {}".format(node))
                else:
                    controller.add_node(node)
                    print("Node created for {}".format(node))
                break
            if user_input == "9":
                node = input("Enter node to be deleted: ")
                if node in controller.graph.nodes:
                    print("Removed node {}".format(node))
                    controller.graph.remove_node(node)
                    #update FT
                    to_delete = []
                    for src in controller.flow_table:
                        if src == node:
                            to_delete.append(src)
                        else:
                            if node in controller.flow_table[src]:
                                del controller.flow_table[src][node]

                    for src in to_delete:
                        del controller.flow_table[src]
                else:
                    print("Node does not exist")

            if user_input == "7":
                print("Please choose one of the following:\n(1) Find the shortest path "
                      "between two nodes.\n(2) Print the flow table.\n(3) Simulate a link failure\n"
                      "(4) Fix/create link.\n(5) Print current topology.\n(6) Create a Topology diagram.\n(7) Print Commands."
                      "\n(8) Create new node.\n(9) Delete node.\n(10) Exit.")
            if user_input == "10":
                exit()
            if user_input not in ["1","2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                print("Command not valid")

