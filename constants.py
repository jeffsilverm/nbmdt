#! /usr/bin/python3
#
# This file contains constants for the NBMDT
#
from enum import IntEnum, Enum, auto

port = 8722  # Default port that the server listens on.  Provides a RESTful interface


class Modes(IntEnum):
    BOOT = 1
    MONITOR =  2
    DIAGNOSE =  3
    TEST =  4
    NOMINAL =  5


class Descriptions(Enum):
    CURRENT = auto()
    NOMINAL = auto()
    NAMED = auto()

    def __init__ (self, description ) -> None :
        assert isinstance(description, Descriptions), f"description is of " \
                                                      f"type {str(type(description))} but " \
                                                      f"should be Descriptions "
        self.description = description

    def is_current(self) -> bool:
        return self.description == self.CURRENT

    def is_nominal(self) -> bool:
        return self.description == self.NOMINAL

    def is_named(self) -> bool:
        return self.description == self.NAMED


class ErrorLevels(IntEnum):
    """
    From The_Network_Boot_Monitor_Diagnostic_Tool.html

        Normal
    All is well.  The resource is working properly in all respects
        Slow
    The monitor is measuring traffic flow through the resource or the delay required to reach the interface, and it is
    outside acceptable limits.  The interface is still working.
        Degraded due to an upstream dependency failure.
    The resource is at increased risk of failure because a dependency is down.  However, the dependency has some
    redundancy so the fact that there is an upstream failure does not mean that this interface is down.  For example,
    there are multiple DNS servers.  If a single server fails, the resolver will pick a different name server.  So DNS
    will work, but there will be fewer servers than normal and a greater risk of subsequent failure.
        Down cause unknown
    The resource is flunking a health check for some reason.
        Down due to a missing or failed dependency
    The resource is flunking a health check or is down because something it depends on is down.
        Down Acknowledged
    The resource is down and an operator has acknowledged that the interface is down.  This will only happen while
    monitoring, never at boot time or while diagnosing or designing
        Changed
    The resource is in the configuration file, but the monitor cannot find it, or the auto configuration methods found
    a resource that should be in the configuration file, but isn't.  Classic example is a NIC changing its MAC address.
        Other problem
    Something else is wrong that doesn't fit into the above categories.

    """

    NORMAL = 1  # Everything is working properly
    SLOW = 2  # Up, but running slower than allowed
    DEGRADED = 3  # Up, but something that this thing partly depends on is down (e.g. 1 DNS server or 1 NTP
    #  server)
    DOWN = 4  # It flunks the test, cause unknown
    DOWN_DEPENDENCY = 5  # It flunks the test, but it is known to be due to a dependency
    DOWN_ACKNOWLEDGED = 6  # It flunks the test, but somebody has acknowledged the problem
    CHANGED = 7  # The resource works, but something about it has changed
    OTHER = 8  # A problem that doesn't fit into any of the above categories
    UNKNOWN = 9  # We genuinely do not know the status of the entity, either because the test has not been
    # run yet or conditions are such that the test cannot be run correctly.


# If termcolor isn't good enough (it has only 8 colors), try colored (which has 256),
# https://pypi.python.org/pypi/colored/1.3.3.  Do not confuse the colored package with
# termcolor.colored
colors = {ErrorLevels.NORMAL:          ['black', 'on_green'], ErrorLevels.SLOW: ['black', 'on_yellow'],
          ErrorLevels.DEGRADED:        ['black', 'on_magenta'], ErrorLevels.DOWN: ['black', 'on_red'],
          ErrorLevels.DOWN_DEPENDENCY: ['black', 'on_cyan'], ErrorLevels.DOWN_ACKNOWLEDGED: ['black', 'on_magenta'],
          ErrorLevels.CHANGED:         ['white', 'on_black'], ErrorLevels.OTHER: ['black', 'on_grey']}
# on is down
# it as
