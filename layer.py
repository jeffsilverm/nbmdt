import constants
import datetime

class Layer(object):

    def __init__(self) -> None:
        self.time = datetime.datetime.now()

    def get_status(self) -> constants.ErrorLevels:
        return constants.ErrorLevels.NORMAL
