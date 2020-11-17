import unittest
import sys
import networkx as nx
import osmnx as ox

sys.path.insert(1, './controller')
sys.path.insert(1, './model')
sys.path.insert(1, './view')

from controller import Controller
from model import Model
from view import View

class test_suite(unittest.TestCase):

    # Compare ascents of walking route between shortest length path and our minimum elevation path
    def test_compare_routes_min_walk(self):
        model = Model()
        controller = Controller()
        view = View()
        model.set_view(view)

        controller.start_lat = 42.4096
        controller.start_long = -72.5352
        controller.end_lat = 42.3510
        controller.end_long = -72.5338
        controller.extra_travel = 50
        controller.mode = 'minimize'
        controller.model = model
        controller.travel_type = 'Walking'
        controller.G = controller.get_map()
        G = controller.G
        controller.start = ox.get_nearest_node(G, (float(controller.start_lat), float(controller.start_long)))
        origin = controller.start
        controller.end = ox.get_nearest_node(G, (float(controller.end_lat), float(controller.end_long)))
        destination = controller.end

        shortest_path = nx.shortest_path(G, origin, destination, weight='length')
        shortest_path_length = model.get_total_length(G, shortest_path)
        can_travel = ((100.0 + controller.extra_travel) * shortest_path_length) / 100.0
        min_el_path = model.get_op_route(G, origin, destination, can_travel, controller.mode)
        shortest_stats = model.get_elevation_stats(G, shortest_path)
        min_el_stats = model.get_elevation_stats(G, min_el_path)

        controller.model = model

        self.assertTrue(min_el_stats["ascents"] <= shortest_stats["ascents"])

    # Compare ascents of driving route between shortest length path and our minimum elevation path
    def test_compare_routes_min_drive(self):
        model = Model()
        controller = Controller()
        view = View()
        model.set_view(view)

        controller.start_lat = 42.4096
        controller.start_long = -72.5352
        controller.end_lat = 42.3510
        controller.end_long = -72.5338
        controller.extra_travel = 50
        controller.mode = 'minimize'
        controller.model = model
        controller.travel_type = 'Driving'
        controller.G = controller.get_map()
        G = controller.G
        controller.start = ox.get_nearest_node(G, (float(controller.start_lat), float(controller.start_long)))
        origin = controller.start
        controller.end = ox.get_nearest_node(G, (float(controller.end_lat), float(controller.end_long)))
        destination = controller.end

        shortest_path = nx.shortest_path(G, origin, destination, weight='length')
        shortest_path_length = model.get_total_length(G, shortest_path)
        can_travel = ((100.0 + controller.extra_travel) * shortest_path_length) / 100.0
        min_el_path = model.get_op_route(G, origin, destination, can_travel, controller.mode)
        shortest_stats = model.get_elevation_stats(G, shortest_path)
        min_el_stats = model.get_elevation_stats(G, min_el_path)

        controller.model = model

        self.assertTrue(min_el_stats["ascents"] <= shortest_stats["ascents"])

    # Compare ascents of biking route between shortest length path and our minimum elevation path
    def test_compare_routes_min_bike(self):
        model = Model()
        controller = Controller()
        view = View()
        model.set_view(view)

        controller.start_lat = 42.4096
        controller.start_long = -72.5352
        controller.end_lat = 42.3510
        controller.end_long = -72.5338
        controller.extra_travel = 50
        controller.mode = 'minimize'
        controller.model = model
        controller.travel_type = 'Biking'
        controller.G = controller.get_map()
        G = controller.G
        controller.start = ox.get_nearest_node(G, (float(controller.start_lat), float(controller.start_long)))
        origin = controller.start
        controller.end = ox.get_nearest_node(G, (float(controller.end_lat), float(controller.end_long)))
        destination = controller.end

        shortest_path = nx.shortest_path(G, origin, destination, weight='length')
        shortest_path_length = model.get_total_length(G, shortest_path)
        can_travel = ((100.0 + controller.extra_travel) * shortest_path_length) / 100.0
        min_el_path = model.get_op_route(G, origin, destination, can_travel, controller.mode)
        shortest_stats = model.get_elevation_stats(G, shortest_path)
        min_el_stats = model.get_elevation_stats(G, min_el_path)

        controller.model = model

        self.assertTrue(min_el_stats["ascents"] <= shortest_stats["ascents"])

    # Compare ascents of biking route between shortest length path and our maximum elevation path
    def test_compare_routes_max_walk(self):
        model = Model()
        controller = Controller()
        view = View()
        model.set_view(view)

        controller.start_lat = 42.4096
        controller.start_long = -72.5352
        controller.end_lat = 42.3510
        controller.end_long = -72.5338
        controller.extra_travel = 50
        controller.mode = 'maximize'
        controller.model = model
        controller.travel_type = 'Walking'
        controller.G = controller.get_map()
        G = controller.G
        controller.start = ox.get_nearest_node(G, (float(controller.start_lat), float(controller.start_long)))
        origin = controller.start
        controller.end = ox.get_nearest_node(G, (float(controller.end_lat), float(controller.end_long)))
        destination = controller.end

        shortest_path = nx.shortest_path(G, origin, destination, weight='length')
        shortest_path_length = model.get_total_length(G, shortest_path)
        can_travel = ((100.0 + controller.extra_travel) * shortest_path_length) / 100.0
        max_el_path = model.get_op_route(G, origin, destination, can_travel, controller.mode)
        shortest_stats = model.get_elevation_stats(G, shortest_path)
        max_el_stats = model.get_elevation_stats(G, max_el_path)

        controller.model = model

        self.assertTrue(max_el_stats["ascents"] >= shortest_stats["ascents"])

    # Compare ascents of biking route between shortest length path and our maximum elevation path
    def test_compare_routes_max_drive(self):
        model = Model()
        controller = Controller()
        view = View()
        model.set_view(view)

        controller.start_lat = 42.4096
        controller.start_long = -72.5352
        controller.end_lat = 42.3510
        controller.end_long = -72.5338
        controller.extra_travel = 50
        controller.mode = 'maximize'
        controller.model = model
        controller.travel_type = 'Driving'
        controller.G = controller.get_map()
        G = controller.G
        controller.start = ox.get_nearest_node(G, (float(controller.start_lat), float(controller.start_long)))
        origin = controller.start
        controller.end = ox.get_nearest_node(G, (float(controller.end_lat), float(controller.end_long)))
        destination = controller.end

        shortest_path = nx.shortest_path(G, origin, destination, weight='length')
        shortest_path_length = model.get_total_length(G, shortest_path)
        can_travel = ((100.0 + controller.extra_travel) * shortest_path_length) / 100.0
        max_el_path = model.get_op_route(G, origin, destination, can_travel, controller.mode)
        shortest_stats = model.get_elevation_stats(G, shortest_path)
        max_el_stats = model.get_elevation_stats(G, max_el_path)

        controller.model = model

        self.assertTrue(max_el_stats["ascents"] >= shortest_stats["ascents"])

    # Compare ascents of biking route between shortest length path and our maximum elevation path
    def test_compare_routes_max_bike(self):
        model = Model()
        controller = Controller()
        view = View()
        model.set_view(view)

        controller.start_lat = 42.4096
        controller.start_long = -72.5352
        controller.end_lat = 42.3510
        controller.end_long = -72.5338
        controller.extra_travel = 50
        controller.mode = 'maximize'
        controller.model = model
        controller.travel_type = 'Biking'
        controller.G = controller.get_map()
        G = controller.G
        controller.start = ox.get_nearest_node(G, (float(controller.start_lat), float(controller.start_long)))
        origin = controller.start
        controller.end = ox.get_nearest_node(G, (float(controller.end_lat), float(controller.end_long)))
        destination = controller.end

        shortest_path = nx.shortest_path(G, origin, destination, weight='length')
        shortest_path_length = model.get_total_length(G, shortest_path)
        can_travel = ((100.0 + controller.extra_travel) * shortest_path_length) / 100.0
        max_el_path = model.get_op_route(G, origin, destination, can_travel, controller.mode)
        shortest_stats = model.get_elevation_stats(G, shortest_path)
        max_el_stats = model.get_elevation_stats(G, max_el_path)

        controller.model = model

        self.assertTrue(max_el_stats["ascents"] >= shortest_stats["ascents"])

if __name__ == '__main__':
    unittest.main()