from tkinter import *
from tkinter.ttk import *
import pickle as pkl
import osmnx as ox


class Controller(Frame):
    def __init__(self, master=Tk()):
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

        Frame.__init__(self)
        master.title("520-EleNa")
        master.resizable(width=False, height=False)
        self.pack(padx=20, pady=20)
        self.create_widgets()

    def set_model(self, model):
        """
        Updates model and route of controller
        """
        self.model = model
        # self.model.get_route(self.G, self.start, self.end,
        #                      self.extra_travel, self.mode)

    def is_number(self, s):
        """
        Determines if valid number
        :param s: (number) Number to be validated
        """
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

    def get_map(self):
        """
        Load in Pickle file of Hampshire County driving map as default.
        Change file based on routing option.
        :return: The selected graph of Hampshire County
        """

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

    def confirm(self, travel_type, mode, start_lat, start_long, end_lat, end_long, extra_travel):
        if not self.is_number(start_lat) or not self.is_number(start_long) or not "." in start_lat or not "." in start_long:
            newWindow = Toplevel(self)
            Label(newWindow,
                  text="Sorry, please enter valid geocoordinate with decimals").pack()
        elif not self.is_number(extra_travel):
            newWindow = Toplevel(self)
            Label(newWindow,
                text="Sorry, please enter a valid number for extra travel").pack()
        else:
            self.start_lat = float(start_lat)
            self.start_long = float(start_long)
            self.end_lat = float(end_lat)
            self.end_long = float(end_long)
            self.extra_travel = float(extra_travel)
            self.mode = mode.lower()
            self.travel_type = travel_type.lower()
            self.G = self.get_map()
            self.start = ox.get_nearest_node(
                self.G, (self.start_lat, self.start_long))
            self.end = ox.get_nearest_node(
                self.G, (self.end_lat, self.end_long))

            self.model.get_route(self.G, self.start, self.end,
                             self.extra_travel, self.mode)

        pass

    def create_widgets(self):
        frame = Frame(self)
        frame.pack(fill=X, side=TOP)

        travel_type_title = Label(frame)
        travel_type_title["text"] = "Please choose your routing type: "
        travel_type_title.pack(side=LEFT)

        travel_type_var = StringVar(frame)
        # travel_type_var.set("Walking")  # default value
        travel_type_options = OptionMenu(
            frame, travel_type_var, "Driving", "Driving", "Walking", "Biking")
        travel_type_options.pack(side=LEFT)
        ##############################
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)

        mode_title = Label(
            frame, text="Would you like to maximize or minimize elevation gain?")
        mode_title.pack(side=LEFT)

        mode_var = StringVar(frame)
        # mode_var.set("Minimize")  # default value
        mode_options = OptionMenu(
            frame, mode_var, "Minimize", "Minimize", "Maximize")
        mode_options.pack(side=LEFT)
        ################################
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)

        start_location_title = Label(
            frame, text="Please enter the Latitude and Longitude of the starting location")
        start_location_title.pack(side=LEFT)
        ################################
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)

        start_lat_title = Label(
            frame, text="Latitude:")
        start_lat_title.pack(side=LEFT)
        start_lat_entry = Entry(frame)
        start_lat_entry.pack(side=LEFT)

        start_long_title = Label(
            frame, text="Longitude:")
        start_long_title.pack(side=LEFT)
        start_long_entry = Entry(frame)
        start_long_entry.pack(side=LEFT)
        ################################
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)

        end_location_title = Label(
            frame, text="Please enter the Latitude and Longitude of the ending location")
        end_location_title.pack(side=LEFT)
        ################################
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)

        end_lat_title = Label(
            frame, text="Latitude:")
        end_lat_title.pack(side=LEFT)
        end_lat_entry = Entry(frame)
        end_lat_entry.pack(side=LEFT)

        end_long_title = Label(
            frame, text="Longitude:")
        end_long_title.pack(side=LEFT)
        end_long_entry = Entry(frame)
        end_long_entry.pack(side=LEFT)
        #################################
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)

        extra_travel_title = Label(
            frame, text="Please enter the percentage of length over the shortest path you are willing to travel")
        extra_travel_title.pack(side=LEFT)
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)
        extra_travel_entry = Entry(frame)
        extra_travel_entry.pack()
        ################################
        frame = Frame(self)
        frame.pack(fill=X, side=TOP, pady=5)
        # sep = Separator()
        # sep.pack()

        button = Button(frame, text="Get route!", command=lambda: self.confirm(
            travel_type_var.get(), mode_var.get(), start_lat_entry.get(), start_long_entry.get(), end_lat_entry.get(), end_long_entry.get(), extra_travel_entry.get()))
        button.pack()
