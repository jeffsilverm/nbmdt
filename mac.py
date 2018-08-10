from constants import ErrorLevels
from layer import Layer

class Mac(object):

    def discover(self):
        pass

    pass

    def __init__(self, name):
        """
        Accepts the name of an interface and returns its MAC address and other characteristics of the physical interface
        :param name:
        """
        self.layer = Layer()

    def get_status(self) -> ErrorLevels :
        return self.layer.get_status()
