import sys

sys.path.insert(1, './controller')
sys.path.insert(1, './model')
sys.path.insert(1, './view')

from controller import Controller
from model import Model
from view import View

class Main(object):

    def __init__(self):
        self.TEST_FLAG = False
        self.run()

    def run(self):
        model = Model()
        controller = Controller()
        view = View()
        model.set_view(view)
        controller.set_model(model)

if __name__ == '__main__':
    model = Main()
