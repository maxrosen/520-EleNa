import sys
import osmnx as ox
import networkx as nx
from heapq import *
import time


class Model(object):

    def set_view(self, vobj):
        self.vobj = vobj

    def get_route(self, G, start, end, extra_travel, mode):
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
        self.vobj.show_route(G, optimized_route, alt_route=[shortest_path])


    def get_op_route(self, G, start, end, can_travel, mode):
        # Uncomment the line below to use the improved max elevation search. I'll make this pretty later 
        self.max_ele = self.get_max_ele_hill_climb
        if(mode == 'maximize'):
            return self.max_ele(G, start, end, can_travel)
        else:
            return self.min_ele(G, start, end, can_travel)

    def max_ele(self, G, start, goal, can_travel):
        shortest_path = nx.shortest_path(G, start, goal, weight='length')
        shortest_path_length = self.get_total_length(G, shortest_path)

        max_path_length = can_travel
        max_path = []
        length_allowance = max_path_length - shortest_path_length
        if (can_travel == shortest_path_length):
            return shortest_path

        for i in range(0, len(shortest_path) - 1):
            cur_node = shortest_path[i]
            next_node = shortest_path[i + 1]
            min_distance = G[cur_node][next_node][0]['length']
            allowance = length_allowance * (min_distance / shortest_path_length)
            highest_elevation = -1
            best_path = []

            for path in nx.all_simple_paths(G, cur_node, next_node, cutoff=10):
                path_elevation = self.get_elevation_stats(G, path)["ascents"]
                path_length = self.get_total_length(G, path)
                if path_elevation > highest_elevation:
                    if path_length <= allowance + min_distance:
                        highest_elevation = path_elevation
                        best_path = path

            best_path_length = self.get_total_length(G, best_path)
            length_allowance -= (best_path_length - min_distance)

            for j in best_path[:-1]:
                max_path.append(j)
        max_path.append(goal)
        return max_path

    def min_ele(self, G, start, goal, can_travel):
        frontier = []
        heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        cost_so_far_ele = {}
        came_from[start] = None
        cost_so_far[start] = 0
        cost_so_far_ele[start] = 0
        while len(frontier) != 0:
            (val, current) = heappop(frontier)
            if current == goal:
                if cost_so_far[current] <= can_travel:
                    break
            for u, next, data in G.edges(current, data=True):
                new_cost = cost_so_far[current] + \
                    self.get_cost(G, current, next)
                new_cost_ele = cost_so_far_ele[current]
                elevationcost = self.get_elevation_cost(G, current, next)
                if elevationcost > 0:
                    new_cost_ele = new_cost_ele + elevationcost
                if next not in cost_so_far_ele or new_cost_ele < cost_so_far_ele[next]:
                    cost_so_far_ele[next] = new_cost_ele
                    cost_so_far[next] = new_cost
                    priority = new_cost_ele
                    heappush(frontier, (priority, next))
                    came_from[next] = current
        return self.get_path(came_from, start, goal)

    def get_max_ele_hill_climb(self, G, start, goal, can_travel):
        
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
                # Filter out the neighbors that are in the path and have no valid neighbors
                if (nbr in curr_path) or (nbr in bad_nodes):
                    continue

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

    def get_elevation_cost(self, G, a, b):
        return (G.nodes[a]['elevation'] - G.nodes[b]['elevation'])

    def get_cost(self, G, a, b):
        edge = G.edges[a, b, 0]
        return edge['length']

    def get_path(self, came_from, origin, destination):
        route_by_length_minele = []
        p = destination
        route_by_length_minele.append(p)
        while p != origin:
            p = came_from[p]
            route_by_length_minele.append(p)
        route_by_length_minele = route_by_length_minele[::-1]
        return route_by_length_minele

    def get_elevation_stats(self, G, route):
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
        if route is None or len(route) <= 1:
            return 0
        cost = 0
        for i in range(len(route)-1):
            cost += self.get_cost(G, route[i], route[i+1])
        return cost

    def print_route_stats(self, G, route):
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
