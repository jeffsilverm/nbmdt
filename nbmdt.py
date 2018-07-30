#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#


# https://pypi.python.org/pypi/termcolor
import optparse
import typing
from typing import Tuple
import sys

import application  # OSI layer 7: HTTP, HTTPS, DNS, NTP
import constants
import interface  # OSI layer 1: ethernet, WiFi
import mac  # OSI layer 2: # Media Access Control: arp, ndp
import network  # OSI layer 3: IPv4, IPv6 should be called network
import presentation  # OSI layer 6:
import session  # OSI layer 5:
import transport  # OSI layer 4: TCP, UDP (and SCTP if it were a thing)

DEBUG = True
type_application_dict = typing.Dict[str, application.Application]
type_presentation_dict = typing.Dict[str, presentation.Presentation]
type_session_dict = typing.Dict[str, session.Session]
type_transport_dict = typing.Dict[str, transport.Transports]
type_network_dict: dict = typing.Dict[str, network.Network]
type_mac_dict = typing.Dict[str, mac.Mac]
type_interface_dict = typing.Dict[str, interface.Interface]

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
    #    CURRENT = None

    def __init__(self, applications: type_application_dict = None,
                 presentations: type_presentation_dict = None,
                 sessions: type_session_dict = None,
                 transports: type_transport_dict = None,
                 networks: type_network_dict = None,
                 macs: type_mac_dict = None,
                 interfaces: type_interface_dict = None,
                 mode=constants.Modes.BOOT,
                 configuration_filename: str = None
                 ) -> None:
        """
        Populate a description of the system.  This discription can come from a file (MONITOR, DIAGNOSE), from the
        current state of the system (BOOT, TEST, NOMINAL).  The description can be displayed colorized and scrolling
        (BOOT), displayed using VT100 (ANSI-X3.64) cursor addressing (MONITOR), or recorded to a configuration file (
        NOMINAL)

        :param applications:
        :param presentations:
        :param sessions:
        :param transports:
        :param networks:
        :param macs:
        :param interfaces:
        :param mode:
        :param configuration_filename:
        """
        # BOOT = 1
        # MONITOR = 2
        # DIAGNOSE = 3
        # TEST = 4
        # NOMINAL = 5
        if mode == constants.Modes.NOMINAL or mode == constants.Modes.BOOT or mode == constants.Modes.TEST:
            # We want to find out what the current state of the system is and record it in a file if
            # in NOMINAL mode or else display it if in BOOT mode
            applications = application.Application.discover()
            presentations = presentation.Presentation.discover()
            sessions = session.Session.discover()
            transports = transport.Transports.discover()
            networks = network.Network.discover()
            macs = mac.Mac.discover()
            interfaces = interface.Interface.discover()
        elif mode == constants.Modes.MONITOR or mode == constants.Modes.DIAGNOSE:
            # Compare the current configuration against a "nominal" configuration in the file and
            # note any changes
            (applications, presentations, sessions, transports, networks, macs, interfaces) = \
                self.read_configuration(configuration_filename)
        elif mode != constants.Modes.NOMINAL:
            raise ValueError(f"mode is {str(mode)} but should be one of BOOT, CURRENT, NAMED, NOMINAL, or TEST")
        self.applications = applications
        self.presentations = presentations
        self.sessions = sessions
        self.transports = transports
        self.networks = networks
        self.mac = macs
        self.interfaces = interfaces
        self.mode = mode

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

    def read_configuration(self, filename):
        # applications, presentations, sessions, transports, networks, macs, interface
        return (None, None, None, None, None, None, None)

    def write_configuration(self, filename):
        return None

    def __str__(self):
        """This generates a nicely formatted report of the state of this system
        This method is probably most useful in BOOT mode"""
        result = application.__str__(mode=self.mode) + "\n" + \
                 presentation.__str__(mode=self.mode) + "\n" + \
                 session.__str__(mode=self.mode) + "\n" + \
                 transport.__str__(mode=self.mode) + "\n" + \
                 network.__str__(mode=self.mode) + "\n" + \
                 mac.__str__(mode=self.mode) + "\n" + \
                 interface.__str__(mode=self.mode)
        return result

from typing import List


def main(args: List[str]):
    sys.argv = args
    # This code must execute unconditionally, because configuration.py has to
    # know if the IP_COMMAND should come from a file or a command
    (options, args_) = arg_parser()
    mode = constants.Modes.BOOT  # For debugging
    current_system = SystemDescription(mode=mode)
    if mode == constants.Modes.BOOT:
        application_status: constants.ErrorLevels = application.get_status()
        presentation_status: constants.ErrorLevels = presentation.get_status()
        session_status: constants.ErrorLevels = session.get_status()
        transport_status: constants.ErrorLevels = transport.get_status()
        network_status: constants.ErrorLevels = network.get_status()
        mac_status: constants.ErrorLevels = mac.get_status()
        interface_status: constants.ErrorLevels = interface.get_status()

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
    parser.add_option('--diagnose', help=
    "Use when a problem is detected. Use TCP port %s by default unless changed by the -p or --port switch" %
    constants.port, action="count", dest="diagnose")
    parser.add_option('--test', help="Test a particular part of the network", action="count", dest="test")
    parser.add_option('--nominal', help="Use when the system is working properly to capture the current state."
                                        "This state will serve as a reference for future testing", action="count",
                      dest="nominal")
    parser.add_option('-p', '--port', type='int', default=constants.port,
                      help='Port where server listens when in monitor mode, default %s' % constants.port)
    (options, args) = parser.parse_args()

    # Select one and only one of these options
    #Look at the arg parser documentation, https://docs.python.org/3/library/argparse.html
    # There is a mechanism in there to make sure that one and only option is selected.
    if (options.boot is None) + (options.monitor is None) + (options.diagnose is None) + \
            (options.test is None) + (options.nominal is None) == 1:
        return options, args
    raise ValueError("Must have exactly one of --boot (or -b), --monitor (or -m), --diagnose (or -d), --nominal (or -N)")

    # As of 2018-07-29, there is a bug: the --debug option is not handled at all

if __name__ == "__main__":
    main(["--boot", "--debug"], )
