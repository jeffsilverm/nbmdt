
from layer import Layer
from constants import ErrorLevels


class Session(object):

    def __init__(self):
        self.layer = Layer()

    def get_status(self) -> ErrorLevels :
        return self.layer.get_status()

    def discover(self):
        pass

    pass
