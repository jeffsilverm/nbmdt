
from layer import Layer
from constants import ErrorLevels


class Session(object):

    def __init__(self, session_str):
        self.session_str = session_str
        self.layer = Layer()

    def get_status(self) -> ErrorLevels :
        return self.layer.get_status()

    @classmethod
    def discover(cls):
        s = cls.__init__(self=cls, session_str="A session string, just a placeholder")
        return s

