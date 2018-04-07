from constants import ErrorLevels
from layer import Layer

class Mac(object):

    def discover(self):
        pass

    pass

    def __init__(self):
        self.layer = Layer()

    def get_status(self) -> ErrorLevels :
        return self.layer.get_status()
