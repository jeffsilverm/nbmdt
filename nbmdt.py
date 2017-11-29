#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#




import subprocess
import socket
import collections
import interfaces
import routes
from routes import IPv4Route as IPv4_route
from routes import IPv6Route as IPv6_route
import networks
import yaml
import termcolor

from enum import Enum
class Modes(Enum):
    BOOT=1
    MONITOR=2
    DIAGNOSE=3
    TEST=4

class ErrorLevels(Enum):
    LABEL=0
    NORMAL=1          # The resource is working properly in all respects
    DEGRADED=2        # The resource is working properly but there are resources it depends on
                      # that are down.  Also, it is slow
    CHANGED=3         # The resource is working, but it doesn't agree with the .ini
                      # file.
    DOWN_ACKED=4      # The resource down problem has been ackowledged
    DOWN_DEPENDENCY=5 # The resource is down because something it depends on is down

    DOWN_UNKNOWN=6    # It's completely not working for unknown reasons

    colors={LABEL: 'grey', NORMAL: 'green', DEGRADED:'yellow', CHANGED:'blue',
            DOWN_ACKED: 'cyan', DOWN_DEPENDENCY: 'magenta', DOWN_UNKNOWN: 'red' }

    if __name__ == '__main__':
        for color in [LABEL, NORMAL, DEGRADED, CHANGED, DOWN_ACKED, DOWN_DEPENDENCY, DOWN_UNKNOWN]:
            termcolor.cprint(colors[color],colors[color] )
        termcolor.cprint('BLINKING red', colors[DOWN_UNKNOWN], attrs=['reverse'] )





class SystemDescription(object):
    """Refer to the OSI stack, for example, at https://en.wikipedia.org/wiki/OSI_model.  Objects of this class describe
     the system, including interfaces, IPv4 and IPv6 addresses, routes, applications.  Each of these objects have a test
     associated with them"""

    def __init__(self, configuration_file=None ):


        if configuration_file==None:
            # This is what the system is currently is

            # Create a dictionary, keyed by link name, of the physical interfaces
            self.link_db = interfaces.PhysicalInterface.get_all_physical_interfaces()
            # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
            self.addr_db = interfaces.LogicalInterface.get_all_logical_interfaces()
            self.routes_4_db = routes.IPv4Route.find_ipv4_routes()
            self.routes_6_db = routes.IPv6Route.find_ipv6_routes()

            #        self.ipv4_routes = addresses.Ipv4Routes()
    #        self.ipv6_routes = addresses.Ipv6Routes()
    #        self.name_servers = nameservers.nameservers()
    #        self.applications = applications
            # To find all IPv4 machines on an ethernet, use arp -a     See ipv4_neighbors.txt

            # To find all IPv6 machines on an ethernet, use ip -6 neigh show
    #        self.networks = networks
    #        self.name = name
        else:
            y = yaml.safe_load(configuration_file)
            self.link_db = y['interfaces']
            self.addr_db = dict()
            for link in self.link_db:
                self.addr_db[link] = y['interface']['ipv4_addr']



    @staticmethod
    def describe_current_state():
        """This method goes through a system that is nominally configured and operating and records the configuration """

#        applications = Applications.find_applications()
#        applications = None
#        ipv4_routes = IPv4_route.find_ipv4_routes()
#        ipv6_routes = IPv6_route.find_ipv6_routes()
#        ipv6_addresses = interfaces.LogicalInterface.find_ipv6_addresses()
#        ipv4_addresses = interfaces.LogicalInterface.find_ipv4_addresses()
#        networks = Networks.find_networks()
#        networks = None

        # nominal = SystemDescription.describe_current_state()



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
        for iface in self.interfaces:
            result += str(iface) + "\n"
        result = result + "\nNetworks:\n" + "*" * 80
        for network in self.networks:
            result += str(network) + "\n"
        return result





if __name__ == "__main__" :
    def boot (self, nominal : SystemDescription, current : SystemDescription ):
        """This method tests the system at boot time.
        """
        results = ErrorLevels.NORMAL
        for interface in current.link_db:
            if interface not in nominal.link_db :
                results = ErrorLevels.CHANGED
            interfaces_status = interface.interfaces_status( )
            if interfaces_status != True :
                results = ErrorLevels.DOWN_UNKNOWN
        for interface in nominal.link_db:
            if interface not in current.link_db:
                # if interface is in current.link_db, then it has already been
                # testerd.
                if ErrorLevels.CHANGED > results :
                    results = ErrorLevels.CHANGED
                interfaces_status = interface.interfaces_status( )
                if interfaces_status != True :
                    results = ErrorLevels.DOWN_UNKNOWN
        return results




    nominal_system_description = SystemDescription ( configuration_file="nominal.txt" )
    current_system_description = SystemDescription ( )

    mode = Modes.BOOT   # This will be an option to the program some day.

    if mode == Modes.BOOT :
         results = boot ( nominal_system_description, current_system_description )
         print()









