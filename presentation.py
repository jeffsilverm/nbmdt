from layer import Layer


class Presentation(Layer):

    def __init__(self):
        self.layer = Layer()

    def get_status(self):
        return self.layer.get_status()

    def discover(self):
        pass
