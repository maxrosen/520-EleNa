import osmnx as ox
import folium
import webbrowser
import time
import itertools
import threading
import sys

class View(object):
    def __init__(self):
        self.done = False

    def show_route(self, G, route, alt_route=None):
        route_coords = []
        for n in route:
            x_coord = str(G.nodes[n]['y'])
            y_coord = str(G.nodes[n]['x'])
            route_coords.append(x_coord + "," + y_coord)

        print()

        directions_url = "https://www.google.com/maps/dir/"
        for c in route_coords:
            directions_url += c + "/"
        # print(directions_url)
        # webbrowser.open(directions_url, new=2)
        # print()

        print("Processing route")
        t = threading.Thread(target=self.loading_animation)
        t.start()

        route_map = ox.plot_route_folium(G, route, route_opacity=0.75, route_color="#42aaf5", tiles='Stamen Terrain')

        #alt_route[0] is networkx's shortest path, weighted by length
        if(len(alt_route)>0):
            ox.plot_route_folium(G, alt_route[0], route_map, route_opacity=0.75, route_color="#eb4034")

        # alt_route[1] is networkx's shortest path, weighted by elevation
        if(len(alt_route)>1):
            ox.plot_route_folium(G, alt_route[1], route_map, route_opacity=0.75, route_color="#fcba03")

        #add our route on top of others
        ox.plot_route_folium(G, route, route_map, route_opacity=0.75, route_color="#42aaf5", tiles='Stamen Terrain')

        #add markers to start and end nodes
        folium.Marker(route_coords[0].split(","), popup='<i>Start</i>', icon=folium.Icon(color='green')).add_to(route_map)
        folium.Marker(route_coords[-1].split(","), popup='<i>End</i>', icon=folium.Icon(color='blue')).add_to(route_map)

        filepath = './route.html'
        route_map.save(filepath)
        # This was broken on windows (and maybe on Mac). We'll fix it later
        # webbrowser.open(filepath, new=2)
        self.done = True
        print('Done!')

    def loading_animation(self):
        for c in itertools.cycle(['.', '..', '...']):
            if self.done:
                break
            sys.stdout.write('\rProcessing route ' + c + '  ')
            sys.stdout.flush()
            time.sleep(0.25)
        sys.stdout.flush()
