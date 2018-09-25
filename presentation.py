from layer import Layer
import constants


class Presentation(Layer):

    def __init__(self, s):
        super().__init__(name="TBD")
        self.presentation = s

    def get_status(self) -> constants.ErrorLevels:
        """

        :rtype: constants.ErrorLevels
        """
        return self.get_status()

    @classmethod
    def discover(cls):
        p = Presentation("A presentation representation string")
        return p

if "__main__" == __name__:
    p = Presentation("BLECH!")
