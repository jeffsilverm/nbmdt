import constants
import datetime

# Read this article: https://simonwillison.net/2021/Nov/4/publish-open-source-python-library/

class Layer(object):

    def __init__(self) -> None:
        self.time = datetime.datetime.now()

    def get_status(self) -> constants.ErrorLevels:
        return constants.ErrorLevels.NORMAL
