import sys
import osmnx as ox
from heapq import *
import pickle as pkl
from pick import pick
import os

sys.path.insert(1, './graphs')

class Controller(object):
    def __init__(self):
        self.start_lat = None
        self.start_long = None
        self.end_lat = None
        self.end_long = None
        self.extra_travel = None
        self.mode = None
        self.model = None
        self.travel_type = None
        self.G = None
        self.start = None
        self.end = None

    def set_model(self, model):
        self.model = model
        self.model.get_route(self.G, self.start, self.end, self.extra_travel, self.mode)

    def is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass
        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False

    def get_inputs(self):
        #Taking input
        os.system('cls' if os.name == 'nt' else 'clear')

        travel_type_title = 'Please choose your routing type: '
        travel_type_options = ['Driving', 'Walking', 'Biking']
        self.travel_type = pick(travel_type_options, travel_type_title)[0].lower()
        print('Selected routing for ' + self.travel_type)
        print()

        mode_title = 'Would you like to maximize or minimize elevation gain?'
        mode_options = ['maximize', 'minimize']
        self.mode = pick(mode_options, mode_title)[0].lower()
        print('Algorithm will ' + self.mode + ' elevation gain')
        print()

        while True:
            start = input("Please enter the Latitude and Longitude of the starting location (separated by a comma) \n")
            if "," not in start:
                print("Sorry, that input did not include a comma")
                continue
            else:
                self.start_lat, self.start_long = start.split(",")
                if self.is_number(self.start_lat) and self.is_number(self.start_long) and "." in self.start_lat and "." in self.start_long:
                    break
                else:
                    print("Sorry, that input is invalid")
                    continue

        print("Latitude of starting location:", float(self.start_lat), "and Longitude of starting location", float(self.start_long))
        print()

        while True:
            end = input("Please enter the Latitude and Longitude of the end location (separated by a comma) \n")
            if "," not in end:
                print("Sorry, that input did not include a comma")
                continue
            else:
                self.end_lat, self.end_long = end.split(",")
                if self.is_number(self.end_lat) and self.is_number(self.end_long) and "." in self.end_lat and "." in self.end_long:
                    break
                else:
                    print("Sorry, that input is invalid")
                    continue

        print("Latitude of end location:", float(self.end_lat), "and Longitude of end location", float(self.end_long))
        print()

        while True:
            self.extra_travel = input("Please enter the percentage of length over the shortest path you are willing to travel \n")
            if self.is_number(self.extra_travel):
                self.extra_travel = float(self.extra_travel)
                break
            else:
                print("Please enter a number")
                continue

        print()

        self.G = self.get_map()
        self.start = ox.get_nearest_node(self.G, (float(self.start_lat), float(self.start_long)))
        self.end = ox.get_nearest_node(self.G, (float(self.end_lat), float(self.end_long)))


    def get_map(self):
        #Load in Pickle file of Hampshire County driving map as default, change based on routing option

        graph_file = "./graphs/graph.pkl"
        if self.travel_type == "driving":
            graph_file = "./graphs/drive_graph.pkl"
        elif self.travel_type == "walking":
            graph_file = "./graphs/walk_graph.pkl"
        elif self.travel_type == "biking":
            graph_file = "./graphs/bike_graph.pkl"

        infile = open(graph_file, 'rb')
        G = pkl.load(infile)
        infile.close()

        return G
