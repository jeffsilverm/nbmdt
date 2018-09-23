import constants
import datetime

class Layer(object):

    def __init__(self, name) -> None:
        self.time = datetime.datetime.now()
        self.name = name

    def get_status(self) -> constants.ErrorLevels:
        return constants.ErrorLevels.NORMAL
