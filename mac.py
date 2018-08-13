from constants import ErrorLevels
from layer import Layer
import enum

class Mac(object):

    class ProtocolName(enum.IntEnum):
        # From https://www.iana.org/assignments/ieee-802-numbers/ieee-802-numbers.xhtml
        IPv6 = 0x86DD       # RFC 7042
        IPv4 = 0x0800       # RFC 7042

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
