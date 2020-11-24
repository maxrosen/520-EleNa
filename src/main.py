import sys

sys.path.insert(1, './controller')
sys.path.insert(1, './model')
sys.path.insert(1, './view')

from controller import Controller
from model import Model
from view import View
# from controller_OLD import Controller

class Main(object):

    def __init__(self):
        self.run()

    def run(self):
        """
        Executes program to find optimized route based on user inputs
        """
        model = Model()
        view = View()
        controller = Controller()

        model.set_view(view)
        controller.set_model(model)
        controller.mainloop()

if __name__ == '__main__':
    model = Main()
