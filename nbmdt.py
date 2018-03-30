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
import optparse

import application # OSI layer 7: HTTP, HTTPS, DNS, NTP
import presentation # OSI layer 6:
import session      # OSI layer 5:
import transport   # OSI layer 4: TCP, UDP (and SCTP if it were a thing)
import network      # OSI layer 3: IPv4, IPv6 should be called network
import mac          # OSI layer 2: # Media Access Control: arp, ndp
import interface   # OSI layer 1: ethernet, WiFi
import sys
import constants
from typing import List, Dict, Tuple


DEBUG = True
type_application_dict = Dict[application.Application]
type_presentation_dict = Dict[presentation.Presentation]
type_session_dict = Dict[session.Session]
type_transport_dict = Dict[transport.Transports]
type_network_dict = Dict[network.Network]
type_mac_dict = Dict[mac.Mac]
type_interface_dict = Dict[interface.Interface]


"""
Lev	Device type 	OSI layer   	TCP/IP original	TCP/IP New	Protocols	PDU       Module
7	host	    	Application 	Application	Application		        	Data      nbmdt, dns, ntp
6	host   	    	Presentation	"	    "   "
5	host        	Session	    	"		"   "
4	host    	    Transport   	Transport	Transport	UDP,TCP,SCTP	Segments    
3	router  		Network 		Internet	Network		IPv4, IPv6  	Packets
2	Switch/Bridge	Data link   	Link		Data Link	CSMA/CD,CSMA/CA	Frames
1	hub/repeater	physical        "		    Physical	Ethernet, WiFI	bits

# From http://jaredheinrichs.com/mastering-the-osi-tcpip-models.html


"""

class SystemDescription(object):
    """Refer to the OSI stack, for example, at https://en.wikipedia.org/wiki/OSI_model.  Objects of this class describe
     the system, including interfaces, IPv4 and IPv6 addresses, routes, applications.  Each of these objects have a test
     associated with them"""

    # Issue 13
    CURRENT = None

# Move the contents of class Descriptions into constants.py and class Constants.
    class Descriptions(Enum):
        CURRENT = auto()
        NOMINAL = auto()
        NAMED = auto()

        def is_current(super) -> bool:
            return super.description == constants.Modes.CURRENT

        def is_nominal(super) -> bool:
            return super.description == constants.Modes.NOMINAL

        def is_named(super) -> bool:
            return super.description == constants.Modes.NAMED


    def __init__(self, applications : type_application_dict = None,
                 presentations : type_presentation_dict = None,
                 sessions : type_session_dict = None,
                 transports : type_transport_dict = None,
                 networks : type_network_dict = None,
                 macs : type_mac_dict = None,
                 interfaces : type_interface_dict = None,
                 mode = CURRENT,
                 configuration_filename : str = None
                 ):

        if mode == SystemDescription.CURRENT:
# We want to find out what the current state of the system is, regardless of what it is supposed to be
            applications = application.discover()
            presentations = presentation.discover()
            sessions = session.discover()
            transports = transport.discover()
            networks = network.discover()
            macs = mac.discover()
            interfaces = interface.discover()
        elif mode == SystemDescription.NAMED:
            (applications, presentations, sessions, transports, networks, macs, interfaces) = \
                self.read_configuration (configuration_filename)
        elif mode != SystemDescription.NOMINAL:
            raise ValueError("mode is %s but should be one of CURRENT, NAMED, or NOMINAL" % mode)
        self.applications = applications
        self.presentations = presentations
        self.sessions = sessions
        self.transports = transports
        self.networks = networks
        self.mac = macs
        self.interfaces = interfaces
        self.mode = mode


    def read_configuration(self, filename):
        pass

    def write_configuration(self, filename):
        pass




    """
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
    
    """
    """
        @staticmethod
        def describe_current_state():
            "This method goes through a system that is nominally configured and operating and records the configuration
            "
    
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
    """
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

def main(args):
    # This code must execute unconditionally, because configuration.py has to
    # know if the IP_COMMAND should come from a file or a command
    mode = constants.Modes.NOMINAL   # For debugging
    current_system = SystemDescription(mode)
    """
    current_system_str = str(current_system)
    print(current_system_str)
    # Issue 9
    current_system.default_ipv4_gateway : network.IPv4Address = network.IPv4Route.get_default_ipv4_gateway()
    assert isinstance(current_system.default_ipv4_gateway, network.IPv4Address), \
        f"network.IPv4Route.get_default_ipv4_gateway return a {type(current_system.default_ipv4_gateway)}, " \
        "should have returned a network.IPv4Address"
    current_system.default_ipv6_gateway = network.IPv6Route.get_default_ipv6_gateway()
    # Issue 14
    assert isinstance(current_system.default_ipv6_gateway, network.IPv6Address), \
        f"network.IPv6Route.get_default_ipv6_gateway returned a {type(current_system.default_ipv6_gateway)}, " \
        "should have returned a network.IPv6Address"
    if current_system.default_ipv4_gateway.ping4():
        cprint("default IPv4 gateway pingable", "green", file=sys.stderr)
    else:
        cprint("default IPv4 gateway is NOT pingable", "red", file=sys.stderr)
    if current_system.default_ipv6_gateway.ping6():
        cprint("default IPv6 gateway pingable", "green", file=sys.stderr)
    else:
        cprint("default IPv6 gateway is NOT pingable", "red", file=sys.stderr)

    nominal_system_description = SystemDescription ( configuration_file="nominal.txt" )
    current_system_description = SystemDescription ( )
    
    mode = Modes.TEST   # This will be an option to the program some day.
    
    if mode == Modes.TEST :
        test ( nominal_system_description, current_system_description )
    """

def arg_parser() -> Tuple:
    parser = optparse.OptionParser()
    parser.add_option('--boot', help="Use at boot time.  Outputs messages color coded with status of network "
                                     "subsystems, and then exits", action="count", dest="boot")
    parser.add_option('--monitor', help="Use while system is running.  Presents a RESTful API that a client can use to "
                                        "monitor the state of the network on a host", action="count", dest="monitor")
    parser.add_option('--diagnose', help=f"Use when a problem is detected. Use TCP port {constants.port} by default "
                                        "unless changed by the -p or --port switch", action="count", dest="diagnose")
    parser.add_option('-p', '--port', type='int', default=constants.port,
                      help=f'Port where server listens when in monitor mode, default {constants.port}'  )
    (options, args) = parser.parse_args()

    if options.boot + options.monitor + options.diagnose == 1:
        return (options, args)
    raise ValueError ("Must have exactly one of --boot, --monitor, --diagnose")

if __name__ == "__main__":
    args = arg_parser()
    main(args)

