#! /usr/bin/python3
#
# This file contains constants for the NBMDT

# Issue 29 https://github.com/jeffsilverm/nbmdt/issues/29
import typing
import enum
from enum import auto
import sys

PORT: int = 8722  # Default PORT that the server listens on.  Provides a RESTful interface


class Modes(enum.IntEnum):
    BOOT = 1
    MONITOR = 2
    DIAGNOSE = 3
    TEST = 4
    NOMINAL = 5


class OperatingSystems(enum.IntEnum):
    LINUX = 1
    MAC_OS_X = 2
    WINDOWS = 3
    BSD = 4
    OTHER = 3000
    UNKNOWN = 0

    """
    def __str__(self):
        if self == self.LINUX:
            return "Linux"
        elif self == self.MAC_OS_X:
            return "Mac OS X"
        elif self == self.WINDOWS:
            return "Microsoft Windows"
        elif self == self.BSD:
            return "Berkely Software Distribution (BSD)"
        elif self == self.OTHER:
            return "Something else"
        elif self == self.UNKNOWN:
            return "Unknown OS"
        else:
            raise ValueError(f"{self} is an impossible value")
    """


class OSILevels(enum.Enum):
    print("Enter an issue that I changed the values of the constants from "
          "integers to strings for reliability", file=sys.stderr)
    PHYSICAL = "PHYSICAL"
    DATALINK = "DATALINK"
    NETWORK4 = "NETWORK4"
    NETWORK6 = "NETWORK6"
    TRANSPORT = "TRANSPORT"
    SESSION = "SESSION"
    PRESENTATION = "PRESENTATION"
    APPLICATION = "APPLICATION"


class Protocols(enum.Enum):
    # These values are from /etc/protocols
    IP = 0  # IPv4.
    TCP = 6
    UDP = 17
    IPv6 = 41  # is ipv6 in /etc/protocols
    IPv6_route = 43  # is ipv6-route in /etc/protocols
    IPv6_frag = 44  # is ipv6-frag in /etc/protocols


class Layers(enum.IntEnum):
    # This is from the nbmdt_user_manual
    #  ethernet, wifi, ipv4, ipv6, neighbors, dhcp4, dhcp6, router,
    # nameserver,  local_ports, isp_routing, remote_ports.
    ETHERNET = 1
    WIFI = 2
    IPV4 = 3
    IPV6 = 4
    NEIGHBORS = 5
    DHCP4 = 6
    DHCP6 = 7
    ROUTER = 8
    NAMESERVER = 9
    LOCAL_PORTS = 10
    ISP_ROUTING = 11
    REMOTE_PORTS = 12


class Descriptions(enum.Enum):
    CURRENT = auto()
    NOMINAL = auto()
    NAMED = auto()

    def is_current(self, description) -> bool:
        return description == self.CURRENT

    def is_nominal(self, description) -> bool:
        return description == self.NOMINAL

    def is_named(self, description) -> bool:
        return description == self.NAMED


class ErrorLevels(enum.IntEnum):
    """
    From The_Network_Boot_Monitor_Diagnostic_Tool.html

        Normal
    All is well.  The resource is working properly in all respects
        Slow
    The monitor is measuring traffic flow through the resource or the delay
    required to reach the interface, and it is
    outside acceptable limits.  The interface is still working.
        Degraded due to an upstream dependency failure.
    The resource is at increased risk of failure because a dependency is
    down.  However, the dependency has some
    redundancy so the fact that there is an upstream failure does not mean
    that this interface is down.  For example,
    there are multiple DNS servers.  If a single server fails, the resolver
    will pick a different name server.  So DNS
    will work, but there will be fewer servers than normal and a greater risk
    of subsequent failure.
        Down cause unknown
    The resource is flunking a health check for some reason.
        Down due to a missing or failed dependency
    The resource is flunking a health check or is down because something it
    depends on is down.
        Down Acknowledged
    The resource is down and an operator has acknowledged that the interface
    is down.  This will only happen while
    monitoring, never at boot time or while diagnosing or designing
        Changed
    The resource is in the configuration file, but the monitor cannot find
    it, or the auto configuration methods found
    a resource that should be in the configuration file, but isn't.  Classic
    example is a NIC changing its MAC address.
        Other problem
    Something else is wrong that doesn't fit into the above categories.

    """

    NORMAL = 1  # Everything is working properly
    SLOW = 2  # Up, but running slower than allowed
    DEGRADED = 3  # Up, but something that this thing partly depends on is
    # down (e.g. 1 DNS server or 1 NTP
    #  server)
    DOWN = 4  # It flunks the test, cause unknown
    DOWN_DEPENDENCY = 5  # It flunks the test, but it is known to be due to a
    #  dependency
    DOWN_ACKNOWLEDGED = 6  # It flunks the test, but somebody has
    # acknowledged the problem
    CHANGED = 7  # The resource works, but something about it has changed
    OTHER = 8  # A problem that doesn't fit into any of the above categories
    UNKNOWN = 9  # We genuinely do not know the status of the entity, either
    # because the test has not been
    # run yet or conditions are such that the test cannot be run correctly.


# If termcolor isn't good enough (it has only 8 colors), try colored (which
# has 256),
# https://pypi.python.org/pypi/colored/1.3.3.  Do not confuse the colored
# package with
# termcolor.colored
colors = {ErrorLevels.NORMAL: ['black', 'on_green'],
          ErrorLevels.SLOW: ['black', 'on_yellow'],
          ErrorLevels.DEGRADED: ['black', 'on_magenta'],
          ErrorLevels.DOWN: ['black', 'on_red'],
          ErrorLevels.DOWN_DEPENDENCY: ['black', 'on_cyan'],
          ErrorLevels.DOWN_ACKNOWLEDGED: ['black', 'on_magenta'],
          ErrorLevels.CHANGED: ['white', 'on_black'],
          ErrorLevels.OTHER: ['black', 'on_grey']}
# on is down
# it as
MAXINT = 4294967296
LAYERS_LIST = "ethernet,wifi,ipv4,ipv6,neighbors,dhcp4,dhcp6,router," \
              "nameserver,local_ports,isp_routing," \
              "remote_ports,application, presentation,session,transport," \
              "network,datalink,physical"

# Moved here from nbmdt.py Issue 29
# https://github.com/jeffsilverm/nbmdt/issues/29
type_application_dict: dict = typing.Dict[str, "application.Application"]
type_presentation_dict: dict = typing.Dict[str, "presentation.Presentation"]
type_session_dict: dict = typing.Dict[str, "session.Session"]
type_transport_dict: dict = typing.Dict[str, "transport.Transport"]
type_network_4_dict: dict = typing.Dict[str, "route.IPv4Route"]
type_network_6_dict: dict = typing.Dict[str, "route.IPv6Route"]
type_network_dict: dict = typing.Dict[str, "route.IPvRoute"]
type_datalink_dict: dict = typing.Dict[str, "datalink.DataLink"]
type_interface_dict:dict = typing.Dict[
    str, "interface.Interface"]  # Issue 25 re-written
type_physical_dict:dict = typing.Dict[str, "physical.Physical"]  # Issue 29
