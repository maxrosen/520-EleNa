import osmnx as ox
import folium
import webbrowser
import time
import itertools
import threading
import sys
from branca.element import Template, MacroElement


class View(object):
    def __init__(self):
        self.done = False

    def show_route(self, G, route, alt_route=None):
        template = self.get_template()

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
        folium.Marker(route_coords[0].split(","), popup='<i>Start</i>', icon=folium.Icon(color='blue', icon='unchecked')).add_to(route_map)
        folium.Marker(route_coords[-1].split(","), popup='<i>End</i>', icon=folium.Icon(color='green', icon='flag')).add_to(route_map)

        macro = MacroElement()
        macro._template = Template(template)

        route_map.get_root().add_child(macro)

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

    def get_template(self):
        template = """
        {% macro html(this, kwargs) %}

        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>EleNa Project</title>
          <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

          <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
          <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

          <script>
          $( function() {
            $( "#maplegend" ).draggable({
                            start: function (event, ui) {
                                $(this).css({
                                    right: "auto",
                                    top: "auto",
                                    bottom: "auto"
                                });
                            }
                        });
        });

          </script>
        </head>
        <body>


        <div id='maplegend' class='maplegend' 
            style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
             border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

        <div class='legend-title'>Legend</div>
        <div class='legend-scale'>
          <ul class='legend-labels'>
            <li><span style='background:#42aaf5;opacity:0.75;'></span>Our Route</li>
            <li><span style='background:#eb4034;opacity:0.75;'></span>Shortest Length Route</li>

          </ul>
        </div>
        </div>

        </body>
        </html>

        <style type='text/css'>
          .maplegend .legend-title {
            text-align: left;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 90%;
            }
          .maplegend .legend-scale ul {
            margin: 0;
            margin-bottom: 5px;
            padding: 0;
            float: left;
            list-style: none;
            }
          .maplegend .legend-scale ul li {
            font-size: 80%;
            list-style: none;
            margin-left: 0;
            line-height: 18px;
            margin-bottom: 2px;
            }
          .maplegend ul.legend-labels li span {
            display: block;
            float: left;
            height: 16px;
            width: 30px;
            margin-right: 5px;
            margin-left: 0;
            border: 1px solid #999;
            }
          .maplegend .legend-source {
            font-size: 80%;
            color: #777;
            clear: both;
            }
          .maplegend a {
            color: #777;
            }
        </style>
        {% endmacro %}"""
        return template

