import sys
import osmnx as ox
import networkx as nx
from heapq import *
import time

class Model(object):

    def set_view(self, vobj):
        self.vobj = vobj

    def get_route(self, G, origin, destination, extra_travel, mode = 'minimize'):
        shortest_path = nx.shortest_path(G, origin, destination, weight='length')
        print()
        print("Printing Statistics of Shortest path route")
        self.print_route_stats(G, shortest_path)


        shortest_elevation_path = nx.shortest_path(G, origin, destination, weight='elevation')
        print()
        print("Printing Statistics of Shortest Elevation path route")
        self.print_route_stats(G, shortest_elevation_path)

        shortest_path_length = self.getTotalLength(G, shortest_path)
        can_travel = ((100.0 + extra_travel)*shortest_path_length)/100.0
        print()
        print("Distance you are willing to travel : ", can_travel)
        if mode == 'minimize':
            #Strategy1
            t = time.time()
            route_minimize_elevation1 = self.dijkstra_search(G, origin, destination, can_travel, mode='minimize')
            print()
            print ("Dijkstra algorithm took :", time.time()-t, " seconds")
            print("Printing Statistics of our algorithm's minimum Elevation route")
            self.print_route_stats(G, route_minimize_elevation1)
            self.vobj.show_route(G, route_minimize_elevation1, alt_route=[shortest_path, shortest_elevation_path])

    def getelevationcost(self, G_proj, a, b):
        return (G_proj.nodes[a]['elevation'] - G_proj.nodes[b]['elevation'])

    def getcost(self, G_proj, a, b):
        return G_proj.edges[a, b, 0]['length']

    def getpath(self, came_from, origin, destination):
        route_by_length_minele = []
        p = destination
        route_by_length_minele.append(p)
        while p != origin:
           p = came_from[p]
           route_by_length_minele.append(p)
        route_by_length_minele = route_by_length_minele[::-1]
        return route_by_length_minele

    def getTotalElevation(self, G_proj, route):
        if not route:
            return 0
        elevationcost = 0
        for i in range(len(route)-1):
             elevationData = self.getelevationcost(G_proj, route[i], route[i+1])
             if elevationData > 0:
                 elevationcost += elevationData
        return elevationcost

    def getTotalLength(self, G_proj, route):
        if not route:
            return 0
        cost = 0
        for i in range(len(route)-1):
             cost += self.getcost(G_proj, route[i], route[i+1])
        return cost

    def dijkstra_search(self, graph, start, goal, viablecost, mode='minimize'):
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
                if cost_so_far[current] <= viablecost:
                    break
            for u, next, data in graph.edges(current, data=True):
                new_cost = cost_so_far[current] + self.getcost(graph, current, next)
                new_cost_ele = cost_so_far_ele[current]
                elevationcost = self.getelevationcost(graph, current, next)
                if elevationcost > 0:
                    new_cost_ele = new_cost_ele + elevationcost
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far_ele[next] = new_cost_ele
                    cost_so_far[next] = new_cost
                    priority = new_cost_ele
                    if mode=='maximize':
                        priority=priority
                    heappush(frontier, (priority, next))
                    came_from[next] = current
        return self.getpath(came_from, start, goal)

    def print_route_stats(self, G_proj, route):
        route_lengths = ox.utils_graph.get_route_edge_attributes(G_proj, route, 'length')
        print('Total trip distance: {:,.0f} meters'.format(self.getTotalLength(G_proj, route)))
        print('Total elevation change: {:,.0f}'.format(self.getTotalElevation(G_proj, route)))
