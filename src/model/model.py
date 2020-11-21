import sys
import osmnx as ox
import networkx as nx
from heapq import *
import time

class Model(object):

    def set_view(self, vobj):
        """
        Sets the view
        :param vobj: the View object that the value will be set to
        """
        self.vobj = vobj

    def get_route(self, G, start, end, extra_travel, mode):
        """
        Finds a path with elevation maximized or minimized as specified (within a specified path length).
        Also provides statistics in comparison with the shortest route (not accounting for elevation)
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param start: (node) The starting point
        :param goal: (node) The end point 
        :param extra_travel: (number) The percentage over the shortest path length that the user is willing to travel.
        :param mode: ('maximize' or 'mimimize') Specifies if the route should maximize or minimize elevation
        """
        shortest_path = nx.shortest_path(G, start, end, weight='length')
        print()
        print("Printing Statistics of Shortest path route")
        self.print_route_stats(G, shortest_path)

        shortest_path_length = self.get_total_length(G, shortest_path)
        can_travel = ((100.0 + extra_travel)*shortest_path_length)/100.0
        print()
        print('Distance you are willing to travel : {:,.0f} meters'.format(can_travel))

        t = time.time()
        optimized_route = self.get_op_route(G, start, end, can_travel, mode)
        print()
        print("Our algorithm took :", time.time() - t, " seconds")
        print("Printing Statistics of our algorithm's " + mode + "d elevation route")
        self.print_route_stats(G, optimized_route)
        elevation_stats_optimized = self.get_elevation_stats(G, optimized_route)
        elevation_stats_shortest = self.get_elevation_stats(G, shortest_path)
        total_distance_optimized = self.get_total_length(G, optimized_route)
        total_distance_shortest = self.get_total_length(G, shortest_path)
        self.vobj.show_route(G, optimized_route, elevation_stats_optimized, elevation_stats_shortest, total_distance_optimized, total_distance_shortest, alt_route=[shortest_path])


    def get_op_route(self, G, start, end, can_travel, mode):
        """
        Finds a path with elevation maximized or minimized as specified (within a specified path length)
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param start: (node) The starting point
        :param goal: (node) The end point 
        :param can_travel: (number) The maximum langth a valid path is allowed to have in meters
        :param mode: ('maximize' or 'mimimize') Specifies if the route should maximize or minimize elevation
        :return: The minimized/maximized elevation path as a list of nodes
        """
        if(mode == 'maximize'):
            return self.max_ele(G, start, end, can_travel)
        elif(mode == 'minimize'):
            return self.min_ele(G, start, end, can_travel)
        else:
            raise Exception("Invalid mode specified. Valid modes: 'minimize', 'maximize'")

    def max_ele(self, G, start, goal, can_travel):
        """
        Finds a path with elevation maximized (within a specified path length)
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param start: (node) The starting point
        :param goal: (node) The end point 
        :param can_travel: (number) The maximum langth a valid path is allowed to have in meters
        :return: The maximized elevation path as a list of nodes
        """
        # Get the shortest path and its length 
        shortest_path = nx.shortest_path(G, start, goal, weight='length')
        shortest_path_length = self.get_total_length(G, shortest_path)
        
        if (can_travel == shortest_path_length):
            return shortest_path

        curr_path = []
        bad_nodes = []
        curr_node = start
        curr_path.append(curr_node)
        
        while curr_node != goal:
            # Get the neighbors of the current node
            neighbors = G.neighbors(curr_node)

            # Filter the neighbors to find the valid possible next nodes
            valid_neighbors = []
            for nbr in neighbors:
                # Filter out the neighbors that are in the path or are bad (ie: have no valid neighbors)
                if (nbr not in curr_path) and (nbr not in bad_nodes):
                    nbr_goal_path = nx.shortest_path(G, nbr, goal, weight='length')
                    nbr_goal_length = self.get_total_length(G, nbr_goal_path)
                    curr_path_length = self.get_total_length(G, curr_path)
                    curr_nbr_edge_cost = self.get_cost(G, curr_node, nbr)

                    # Append only the nodes that will not cause the path length to be too long
                    if curr_path_length + curr_nbr_edge_cost + nbr_goal_length <= can_travel:
                        valid_neighbors.append(nbr)

            # If a node has no valid neighbors
            if (len(valid_neighbors) == 0):
                # Mark the node as bad
                bad_nodes.append(curr_node)
                # Backtrack on the path
                curr_path = curr_path[:-1]
                # Set the current node to the end of the path (previous node)
                curr_node = curr_path[-1]
            
            # If a node does have valid neighbors
            else:
                # Find the valid neighbor with the highest elevation, add it to the path, and update the current node 
                max_ele_vnbr = valid_neighbors[0]
                for vnbr in valid_neighbors:
                    if G.nodes[vnbr]["elevation"] > G.nodes[max_ele_vnbr]["elevation"]:
                        max_ele_vnbr = vnbr
                curr_path.append(max_ele_vnbr)
                curr_node = max_ele_vnbr

        return curr_path

    def min_ele(self, G, start, goal, can_travel):
        """
        Finds a path with elevation gain minimized (within a specified path length)
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param start: (node) The starting point
        :param goal: (node) The end point 
        :param can_travel: (number) The maximum langth a valid path is allowed to have in meters
        :return: The minimized elevation path as a list of nodes
        """
        frontier = []
        heappush(frontier, (0, start))

        prev_nodes = {}
        prev_nodes[start] = None
        
        curr_costs = {}
        curr_costs[start] = 0

        curr_ele_costs = {}
        curr_ele_costs[start] = 0

        while len(frontier) != 0:
            (val, curr_node) = heappop(frontier)
            if curr_node == goal:
                if curr_costs[curr_node] <= can_travel:
                    break
            
            # Get all edges that are incident to the current node
            for u, next, data in G.edges(curr_node, data=True):
                new_cost = curr_costs[curr_node] + self.get_cost(G, curr_node, next)
                new_ele_cost = curr_ele_costs[curr_node]
                elevationcost = self.get_elevation_cost(G, curr_node, next)

                if elevationcost > 0:
                    new_ele_cost = new_ele_cost + elevationcost

                # If next is an unexplored node or if the current path has a 
                # lower elevation cost than any other path to next
                if next not in curr_ele_costs or new_ele_cost < curr_ele_costs[next]:
                    # Update costs
                    curr_ele_costs[next] = new_ele_cost
                    curr_costs[next] = new_cost
                    # Push next onto frontier with updated priority
                    heappush(frontier, (new_ele_cost, next))
                    # Make next the previous node for curr_node
                    prev_nodes[next] = curr_node

        # Get a path from the set of previous nodes
        path = self.get_path_from_prevs(prev_nodes, start, goal)
        return path

    def get_elevation_cost(self, G, start, end):
        """
        Gets the elevation cost between two nodes
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param start: (node) The starting point
        :param end: (node) The end point 
        :return: The elevation cost between the two nodes in meters
        """
        return (G.nodes[start]['elevation'] - G.nodes[end]['elevation'])

    def get_cost(self, G, start, end):
        """
        Gets the cost of an edge between two nodes in meters
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param start: (node) The starting point
        :param end: (node) The end point 
        :return: (number) the cost of the edge between start and end in meters
        """
        edge = G.edges[start, end, 0]
        return edge['length']

    def get_path_from_prevs(self, prev_nodes, start, goal):
        """
        Finds a path from a dictionary of previous nodes
        :param prev_nodes: a dictionary of nodes, indexed by nodes, where each index node points to the preceeding node in a path
        :param start: (node) the starting point of the path
        :param goal: (node) the goal node of the path
        :return: the path as a list of nodes
        """
        route = []
        curr_node = goal
        route.append(curr_node)
        while curr_node != start:
            curr_node = prev_nodes[curr_node]
            route.append(curr_node)
        route = route[::-1]
        return route

    def get_elevation_stats(self, G, route):
        """
        Gathers statistics regarding elevation about a route
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param route: the route as a list of nodes
        :return: a dictionary containing the net elevation change, total elevation gain, total elevation loss, and total elevation change in meters
        """
        if route is None:
            return 0
        elevation_stats = {
            "net_change": 0,
            "ascents": 0,
            "descents": 0,
            "total_change": 0
        }
        for i in range(len(route)-1):
            elevation_change = self.get_elevation_cost(
                G, route[i], route[i+1])
            if elevation_change == 0:
                continue
            if elevation_change > 0:
                elevation_stats["ascents"] += elevation_change
                elevation_stats["total_change"] += elevation_change
            elif elevation_change < 0:
                elevation_stats["descents"] += elevation_change
                elevation_stats["total_change"] += (-elevation_change)
            elevation_stats["net_change"] += elevation_change

        return elevation_stats

    def get_total_length(self, G, route):
        """
        Finds and returns the length of a route, disregarding elevation, in meters
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param route: the route as a list of nodes
        :return: (number) the length of the route in meters
        """
        if route is None or len(route) <= 1:
            return 0
        cost = 0
        for i in range(len(route)-1):
            cost += self.get_cost(G, route[i], route[i+1])
        return cost

    def print_route_stats(self, G, route):
        """
        Prints the statistics about a route, including distance and elevation statistics
        :param G: (networkx MultiDiGraph object) The graph representing the map
        :param route: the route as a list of nodes
        """
        print('Total trip distance: {:,.0f} meters'.format(
            self.get_total_length(G, route)))

        elevation_stats = self.get_elevation_stats(G, route)
        print('Net elevation change: {:,.0f}'.format(
            elevation_stats["net_change"]))
        print('Elevation gain (ascents): {:,.0f}'.format(
            elevation_stats["ascents"]))
        print('Elevation loss (descents): {:,.0f}'.format(
            elevation_stats["descents"]))
        print('Total elevation change: {:,.0f}'.format(
            elevation_stats["total_change"]))
