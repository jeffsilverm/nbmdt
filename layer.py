import constants


class Layer(object):

    def get_status(self) -> constants.ErrorLevels:
        return constants.ErrorLevels.NORMAL
