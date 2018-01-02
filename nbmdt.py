#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#


from enum import Enum, auto
import configuration


import yaml
# https://pypi.python.org/pypi/termcolor
from termcolor import cprint

import applications # OSI layer 7: HTTP, HTTPS
import presentation # OSI layer 6:
import session      # OSI layer 5:
import transports   # OSI layer 4: TCP, UDP (and SCTP if it were a thing)
import network      # OSI layer 3: IPv4, IPv6 should be called network
import mac          # OSI layer 2: # Media Access Control: arp, ndp
import interfaces   # OSI layer 1: ethernet, WiFi

DEBUG = True

"""
Lev	Device type 	OSI layer   	TCP/IP original	TCP/IP New	Protocols	PDU
7	host	    	Application 	Application	Application		        	Data
6	    	    	Presentation	"		"
5		        	Session	    	"		"
4		    	    Transport   	Transport	Transport	UDP,TCP,SCTP	Segments
3	router  		Network 		Internet	Network		IPv4, IPv6  	Packets
2	Switch/Bridge	Data link   	Link		Data Link	CSMA/CD,CSMA/CA	Frames
1	hub/repeater	physical        "		    Physical	Ethernet, WiFI	bits

# From http://jaredheinrichs.com/mastering-the-osi-tcpip-models.html


"""


# If termcolor isn't good enough (it has only 8 colors), try colored (which has 256),
# https://pypi.python.org/pypi/colored/1.3.3.  Do not confuse the colored package with
# termcolor.colored
class Modes(Enum):
    BOOT = 1
    MONITOR = 2
    DIAGNOSE = 3
    TEST = 4
    NOMINAL = 5

class ErrorLevels(Enum):
    """
    From The_Network_Boot_Monitor_Diagnostic_Tool.html


        Normal
    All is well.  The resource is working properly in all respects
        Slow
    The monitor is measuring traffic flow through the resource or the delay required to reach the interface, and it is outside acceptable limits.  The interface is still working.
        Degraded due to an upstream dependency failure.
    The resource is at increased risk of failure because a dependency is down.  However, the dependency has some redundancy so the fact that there is an upstream failure does not mean that this interface is down.  For example, there are multiple DNS servers.  If a single server fails, the resolver will pick a different name server.  So DNS will work, but there will be fewer servers than normal and a greater risk of subsequent failure.
        Down cause unknown
    The resource is flunking a health check for some reason.
        Down due to a missing or failed dependency
    The resource is flunking a health check or is down because something it depends on is down.
        Down Acknowledged
    The resource is down and an operator has acknowledged that the interface is down.  This will only happen while monitoring, never at boot time or while diagnosing or designing
        Changed
    The resource is in the configuration file, but the monitor cannot find it, or the auto configuration methods found a resource that should be in the configuration file, but isn't.  Classic example is a NIC changing its MAC address.
        Other problem
    Something else is wrong that doesn't fit into the above categories.

    """

    NORMAL = 1              # Everything is working properly
    SLOW = 2                # Up, but running slower than allowed
    DEGRADED = 3            #  Up, but something that this thing partly depends on is down
    DOWN = 4                # It flunks the test, cause unknown
    DOWN_DEPENDENCY = 5     # It flunks the test, but it is known to be due to a dependency
    DOWN_ACKNOWLEDGED = 6   # It flunks the test, but somebody has acknowledged the problem
    CHANGED = 7             # The resource works, but something about it has changed
    OTHER = 8               # A problem that doesn't fit into any of the above categories
    UNKNOWN = 9             # We genuinely do not know the status of the entity, either because the test has not been
    # run yet or conditions are such that the test cannot be run correctly.


colors = {}
colors[ErrorLevels.NORMAL] = ['black', 'on_green']
colors[ErrorLevels.SLOW] = ['black', 'on_yellow']
colors[ErrorLevels.DEGRADED] = ['black', 'on_magenta']
colors[ErrorLevels.DOWN] = ['black', 'on_red']
colors[ErrorLevels.DOWN_DEPENDENCY] = ['black', 'on_cyan']
colors[ErrorLevels.DOWN_ACKNOWLEDGED] = ['black', 'on_magenta']
colors[ErrorLevels.CHANGED] = ['white', 'on_black']
colors[ErrorLevels.OTHER] = ['black', 'on_grey']


class SystemDescription(object):
    """Refer to the OSI stack, for example, at https://en.wikipedia.org/wiki/OSI_model.  Objects of this class describe
     the system, including interfaces, IPv4 and IPv6 addresses, routes, applications.  Each of these objects have a test
     associated with them"""

    # Issue 13
    CURRENT = None

    class Descriptions(Enum):
        CURRENT = auto()
        NOMINAL = auto()
        NAMED = auto()

        def is_current(super) -> bool:
            return super.description == SystemDescription.Descriptions.CURRENT

        def is_nominal(super) -> bool:
            return super.description == SystemDescription.Descriptions.NAMED

        def is_named(super) -> bool:
            return super.description == SystemDescription.Descriptions.NAMED




    def __init__(self, configuration_file: str = None, description: Descriptions = None) -> None:

        if configuration_file is None:
            # This is what the system is currently is

            # Create a dictionary, keyed by link name, of the physical interfaces
            self.phys_db = interfaces.PhysicalInterface.get_all_physical_interfaces()
            # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
            self.data_link_db = interfaces.LogicalInterface.get_all_logical_interfaces()
            # Create lists, sorted from smallest netmask to largest netmask of IPv4 and IPv6 routes
            self.ipv4_routes = network.IPv4Route.find_ipv4_routes()
            self.default_ipv4_gateway : network.IPv4Address = network.IPv4Route.get_default_ipv4_gateway()
            self.ipv6_routes = network.IPv6Route.find_ipv6_routes()
            self.default_ipv6_gateway : network.IPv6Address = network.IPv6Route.get_default_ipv6_gateway()
            # Create something... what?  to track transports (OSI layer 4)
            self.transports_4 = transports.ipv4
            self.transports_6 = transports.ipv6
            # Issue 13
            if description is None or description == self.Descriptions.CURRENT:
                # Assume current
                self.description = self.Descriptions.CURRENT


        else:
            raise NotImplemented("configuration file is not implemented yet")

        if not hasattr(self, "IP_COMMAND"):
            self.IP_COMMAND = configuration.Configuration.find_executable('ip')
        if not hasattr(self, "PING4_COMMAND"):
            self.PING4_COMMAND = configuration.Configuration.find_executable('ping')
        if not hasattr(self, "PING6_COMMAND"):
            self.PING6_COMMAND = configuration.Configuration.find_executable('ping6')
        if DEBUG:
            import os
            assert os.stat.S_IXUSR & os.stat(os.path)[os.stat.ST_MODE]
            assert os.stat.S_IXUSR & os.stat(os.path)[os.stat.ST_MODE]




            self.applications: dict = {}  # For now

            #        self.name_servers = nameservers.nameservers()
            #        self.applications = applications
            # To find all IPv4 machines on an ethernet, use arp -a     See ipv4_neighbors.txt

            # To find all IPv6 machines on an ethernet, use ip -6 neigh show
            #        self.networks = networks
            #        self.name = name
        else:
            y = yaml.safe_load(configuration_file)
            self.interfaces = y['interfaces']
            for interface in self.interfaces:
                self.ipv4_address = interfaces

    @staticmethod
    def describe_current_state():
        """This method goes through a system that is nominally configured and operating and records the configuration
        """

        #        applications = Applications.find_applications()
        #        applications = None
        #        ipv4_routes = IPv4_route.find_ipv4_routes()
        #        ipv6_routes = IPv6_route.find_ipv6_routes()
        #        ipv6_addresses = interfaces.LogicalInterface.find_ipv6_addresses()
        #        ipv4_addresses = interfaces.LogicalInterface.find_ipv4_addresses()
        #        networks = Networks.find_networks()
        #        networks = None

        # nominal = SystemDescription.describe_current_state()
        pass

    #        return (applications, ipv4_routes, ipv6_routes, ipv4_addresses, ipv6_addresses, networks)

    def __str__(self):
        """This generates a nicely formatted report of the state of this system"""
        result = "Applications:\n" + "*" * 80
        for app in self.applications:
            result += str(app) + "\n"
        result = result + "\nIPv4 routes\n" + "*" * 80
        for r4 in self.ipv4_routes:
            result += str(r4) + "\n"
        result = result + "\nIPv6 routes\n" + "*" * 80
        for r6 in self.ipv6_routes:
            result += str(r6) + "\n"
        result = result + "\ninterfaces\n" + "*" * 80
        for iface in self.data_link_db:
            result += str(iface) + "\n"
        return result


# This code must execute unconditionally, because configuration.py has to
# know if the IP_COMMAND should come from a file or a command
mode = Modes.NOMINAL  # For debugging
current_system = SystemDescription(SystemDescription.CURRENT)
current_system_str = str(current_system)
print(current_system_str)
current_system.default_ipv4_gateway = network.IPv4Route.get_default_ipv4_gateway()
assert isinstance(current_system.default_ipv4_gateway, network.IPv4Address), \
    f"network.IPv4Route.get_default_ipv4_gateway return a {type(current_system.default_ipv4_gateway)}, " \
    "should have returned a network.IPv4Address"
current_system.default_ipv6_gateway = network.IPv6Route.get_default_ipv6_gateway()
# Issue 14
assert isinstance(current_system.default_ipv6_gateway, network.IPv6Address), \
    f"network.IPv6Route.get_default_ipv6_gateway returned a {type(current_system.default_ipv6_gateway)}, " \
    "should have returned a network.IPv6Address"
if current_system.default_ipv4_gateway.ping4():
    cprint("default IPv4 gateway pingable", "green")
else:
    cprint("default IPv4 gateway is NOT pingable", "red")
if current_system.default_ipv6_gateway.ping6():
    cprint("default IPv6 gateway pingable", "green")
else:
    cprint("default IPv6 gateway is NOT pingable", "red")

"""
nominal_system_description = SystemDescription ( configuration_file="nominal.txt" )
current_system_description = SystemDescription ( )

mode = Modes.TEST   # This will be an option to the program some day.

if mode == Modes.TEST :
    test ( nominal_system_description, current_system_description )
"""
