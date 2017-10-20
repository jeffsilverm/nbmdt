#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#




import subprocess
import socket
import collections
import routes
from routes import IPv4Route as IPv4_route
from routes import IPv6Route as IPv6_route
import interfaces
import yaml


from enum import Enum
class Modes(Enum):
    BOOT=1
    MONITOR=2
    DIAGNOSE=3
    TEST=4

class ErrorLevels(Enum):
    OKAY=1         # Everything is working properly
    DEGRADED=2     # Many things are working properly
    CHANGED=3      # Things are working but they aren't what's in the database
    UNKNOWN=4      # The program can't tell if something is working or not
    DOWN=5         # It's completely not working

import termcolor
    colors={}
    colors[OKAY] = termcolor.COLORS.mpl

class Networks(object):
    def __init__(self):
        self.remote_hosts = []

    @staticmethod
    def find_networks():
        pass


class Applications(object):
    def __init__(self):
        self.applications = []

    @staticmethod
    def find_applications():
        pass


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
            self.routes_4_db = routes.Routes.get_all_ipv4_routes()
            self.routes_6_db = routes.Routes.get_all_ipv4_routes()

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
            self.interfaces = y['interfaces']
            for interface in self.interfaces:
                self.ipv4_address = interfaces


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
    nominal_system_description = SystemDescription ( configuration_file="nominal.txt" )
    current_system_description = SystemDescription ( )

    mode = Modes.TEST   # This will be an option to the program some day.

    if mode == Modes.TEST :
        test ( nominal_system_description, current_system_description )









