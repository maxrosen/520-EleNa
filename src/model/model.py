import sys
import osmnx as ox
import networkx as nx
from heapq import *
import time


class Model(object):

    def set_view(self, vobj):
        self.vobj = vobj

    def get_route(self, G, origin, destination, extra_travel, mode='minimize'):
        shortest_path = nx.shortest_path(
            G, origin, destination, weight='length')
        print()
        print("Printing Statistics of Shortest path route")
        self.print_route_stats(G, shortest_path)

        shortest_elevation_path = nx.shortest_path(
            G, origin, destination, weight='elevation')
        print()
        print("Printing Statistics of Shortest Elevation path route")
        self.print_route_stats(G, shortest_elevation_path)

        shortest_path_length = self.get_total_length(G, shortest_path)
        can_travel = ((100.0 + extra_travel)*shortest_path_length)/100.0
        print()
        print("Distance you are willing to travel : ", can_travel)

        # Strategy1
        t = time.time()
        route_minimize_elevation1 = self.dijkstra_search(G, origin, destination, can_travel, mode)
        print()
        print("Dijkstra algorithm took :", time.time()-t, " seconds")
        print("Printing Statistics of our algorithm's minimum Elevation route")
        self.print_route_stats(G, route_minimize_elevation1)
        self.vobj.show_route(G, route_minimize_elevation1, alt_route=[
                             shortest_path, shortest_elevation_path])

    def get_elevation_cost(self, G, a, b):
        return (G.nodes[a]['elevation'] - G.nodes[b]['elevation'])

    def get_cost(self, G, a, b):
        return G.edges[a, b, 0]['length']

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
        if route is None:
            return 0
        cost = 0
        for i in range(len(route)-1):
            cost += self.get_cost(G, route[i], route[i+1])
        return cost

    def dijkstra_search(self, G, start, goal, viablecost, mode='minimize'):
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
            for u, next, data in G.edges(current, data=True):
                new_cost = cost_so_far[current] + \
                    self.get_cost(G, current, next)
                new_cost_ele = cost_so_far_ele[current]
                elevationcost = self.get_elevation_cost(G, current, next)
                if elevationcost > 0:
                    new_cost_ele = new_cost_ele + elevationcost
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far_ele[next] = new_cost_ele
                    cost_so_far[next] = new_cost
                    priority = new_cost_ele
                    if mode == 'maximize':
                        priority = priority
                    heappush(frontier, (priority, next))
                    came_from[next] = current
        return self.get_path(came_from, start, goal)

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
