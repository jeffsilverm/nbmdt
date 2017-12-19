#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#




from enum import Enum

from termcolor import colored
import yaml

import interfaces
import routes
import network
import tests
import transports
import applications


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
    DOWN_DEPENDENCY = 5     # It flunks the test, but it is known to be due
# to a dependency
    DOWN_ACKNOWLEDGED = 6   # It flunks the test, but somebody has
# acknowledged the problem
    CHANGED = 7             # The resource works, but something about it has changed
    OTHER = 8               # A problem that doesn't fit into any of the above categories



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

    def __init__(self, configuration_file: str = None) -> None:

        if configuration_file is None:
            # This is what the system is currently is

            # Create a dictionary, keyed by link name, of the physical interfaces
            self.phys_db = interfaces.PhysicalInterface.get_all_physical_interfaces()
            # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
            self.data_link_db = interfaces.LogicalInterface.get_all_logical_interfaces()
            # Create lists, sorted from smallest netmask to largest netmask of IPv4 and IPv6 routes
            self.ipv4_routes = routes.IPv4Route.find_ipv4_routes()
            self.default_ipv4_gateway = routes.IPv4Route.get_default_ipv4_gateway()
            self.ipv6_routes = routes.IPv6Route.find_all_ipv6_routes()
            self.default_ipv6_gateway = routes.IPv6Route.get_default_ipv6_gateway()
            # Create something... what?  to track transports (OSI layer 4)
            self.transports_4 = transports.ipv4
            self.transports_6 = transports.ipv6

            self.applications = {}   # For now

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

    def test_default_ipv4_gateway (self ):
        default_ipv4_gateway = self.default_ipv4_gateway
        ping_results = tests.Tests.ping4( default_ipv4_gateway, count=5, min_for_good=4, slow_ms=40.0 )
        return ping_results


    def test (self ):
        pass



if __name__ == "__main__":

    mode = Modes.NOMINAL    # For debugging
    current_system = SystemDescription()
    current_system_str = str(current_system)
    print ( current_system_str )
    default_ipv4_gateway = routes.IPv4Route.get_default_ipv4_gateway()
    default_ipv6_gateway = routes.IPv6Route.get_default_ipv6_gateway()
    if current_system.test_default_ipv4_gateway() :
        colored.cprint("default IPv4 gateway pingable", "green")
    else:
        colored.cprint("default IPv4 gateway is NOT pingable", "red")



"""
    nominal_system_description = SystemDescription ( configuration_file="nominal.txt" )
    current_system_description = SystemDescription ( )

    mode = Modes.TEST   # This will be an option to the program some day.

    if mode == Modes.TEST :
        test ( nominal_system_description, current_system_description )
"""
