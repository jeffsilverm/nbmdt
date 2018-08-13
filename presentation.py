from layer import Layer


class Presentation(Layer):

    def __init__(self, s):
        self.presentation = s
        self.layer = Layer()

    def get_status(self):
        return self.layer.get_status()

    @classmethod
    def discover(cls):
        p = cls.__init__(self=cls, s="A presentation representation string")
        return p
