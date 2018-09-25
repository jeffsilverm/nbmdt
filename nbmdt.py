#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#


# https://pypi.python.org/pypi/termcolor
import argparse
import json
import platform
import sys
import typing
from typing import List
from typing import Tuple

import application  # OSI layer 7: HTTP, HTTPS, DNS, NTP
import constants
# from physical import Physical
# import interface  # OSI layer 2: ethernet, WiFi       # issue 25
import datalink  # OSI layer 2: # Media Access Control: arp, ndp
import network  # OSI layer 3: IPv4, IPv6 should be called network, routing
import physical  # OSI layer 1: Hardware: ethernet, WiFi, RS-232, etc.
import presentation  # OSI layer 6:
import session  # OSI layer 5:
import transport  # OSI layer 4: TCP, UDP (and SCTP if it were a thing)

DEBUG = True
try:
    print("Testing the __file__ special variable: " + __file__, file=sys.stderr)
except Exception as e:  # if anything goes wrong
    print("Testing the __file__ special variable FAILED, exception is " + str(e), file=sys.stderr)
type_application_dict = typing.Dict[str, application.Application]
type_presentation_dict = typing.Dict[str, presentation.Presentation]
type_session_dict = typing.Dict[str, session.Session]
type_transport_dict = typing.Dict[str, transport.Transport]
type_network_dict: dict = typing.Dict[str, network.Network]
type_datalink_dict = typing.Dict[str, datalink.DataLink]
# type_interface_dict = typing.Dict[str, interface.Interface]   # Issue 25
try:
    type_physical_dict = typing.Dict[str, physical.Physical]
except AttributeError as e:
    print(f"physical.Physical is raising an Attribute error.  {dir(physical)}",
          f"physical is in file {physical.__file__} . ", file=sys.stderr)

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

options = None
LAYERS_LIST = "ethernet,wifi,ipv4,ipv6,neighbors,dhcp4,dhcp6,router,nameserver,local_ports,isp_routing," \
              "remote_ports,application, presentation,session,transport,network,datalink,physical"


class SystemDescription(object):
    """Refer to the OSI stack, for example, at https://en.wikipedia.org/wiki/OSI_model.  Objects of this class describe
     the system, including devices, datalinks, IPv4 and IPv6 addresses and routes, TCP and UDP, sessions,
     presentations, applications.  Each of these objects have a test associated with them"""

    # Issue 13
    #    CURRENT = None

    def __init__(self, applications: type_application_dict = None,
                 presentations: type_presentation_dict = None,
                 sessions: type_session_dict = None,
                 transports: type_transport_dict = None,
                 networks: type_network_dict = None,
                 # interfaces: type_interface_dict = None,          # Issue 25
                 datalinks: type_datalink_dict = None,
                 physicals: type_physical_dict = None,
                 mode: constants.Modes = constants.Modes.BOOT,
                 configuration_filename: str = None,
                 system_name: str = platform.node()
                 ) -> None:
        """
        Populate a description of the system.  Note that this method is
        a constructor, and all it does is create a SystemDescription object.

        :param applications:
        :param presentations:
        :param sessions:
        :param transports:
        :param networks:
        :param datalinks:
        :param mode:
        :param configuration_filename:
        :param system_name: str The name of this computer
        """
        self.applications = applications
        self.presentations = presentations
        self.sessions = sessions
        self.transports = transports  # TCP, UDP
        self.networks = networks  # IPv4, IPv6
        self.datalinks = datalinks  # MAC address
        self.physicals = physicals
        self.mode = mode
        self.configuration_filename: str = configuration_filename
        self.system_name = system_name

    @classmethod
    def system_description_from_file(cls, filename: str) -> 'SystemDescription':
        """
        Read a system description from a file and create a SystemDescription object.
        I couldn't figure out how to return a SystemDescription object, so I return an object
        :param filename:
        :return:
        """

        with open(filename, "r") as f:
            so = json.load(f)

        return SystemDescription(
            applications=so.applications,
            presentations=so.presentations,
            sessions=so.presentations,
            transports=so.transports,
            networks=so.networks,
            datalinks=so.datalinks,
            physicals=so.physicals,
            mode=so.mode,
            configuration_filename=filename,
            system_name=so.system_name
        )

    @classmethod
    def discover(cls) -> object:
        """

        :return: a SystemDescription object.
        """

        applications: typing.Dict = application.Application.discover()
        presentations = presentation.Presentation.discover()
        sessions = session.Session.discover()
        transports = transport.Transport.discover()
        networks = network.Network.discover()
        # interfaces = interface.Interface.discover()
        datalinks = datalink.DataLink.discover()
        physicals = physical.Physical.discover()
        name: str = platform.node()

        my_system: object = SystemDescription(
            applications=applications,
            presentations=presentations,
            sessions=sessions,
            transports=transports,
            networks=networks,
            datalinks=datalinks,
            physicals=physicals,
            system_name=name
        )
        return my_system

    def file_from_system_description(self, filename: str) -> None:
        """Write a system description to a file
        :param  filename
        :return:
        """
        # In the future, detect if a configuration file already exists, and if so, create
        # a new version.
        with open(filename, "w") as f:
            json.dump(self, f)

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

    @property
    def __str__(self):
        """This generates a nicely formatted report of the state of this system
        This method is probably most useful in BOOT mode.

        The classes should be re-written with __str__ methods which are sensitive to the mode
        """
        result = str( self.applications ) + "\n" + \
                 str( self.presentations ) + "\n" + \
                 str( self.sessions ) + "\n" + \
                 str( self.transports ) + "\n" + \
                 str( self.networks ) + "\n" + \
                 str( self.datalinks )
        return result

    def diagnose(self, nominal_system) -> constants.ErrorLevels:
        raise NotImplementedError

    def monitor(self) -> None:
        raise NotImplementedError

    def nominal(self, filename) -> None:
        self.file_from_system_description(filename)

    def test(self) -> constants.ErrorLevels:
        raise NotImplementedError

    def boot(self) -> constants.ErrorLevels:
        raise NotImplementedError


def main(args: List[str] = None):
    """
    Parse arguments, decide what mode to work in.
    :param args: a list of options,perhaps passed by a debugger.
    :return:
    """

    global options, mode
    if args is not None:
        sys.argv.extend(args)
    # This code must execute unconditionally, because configuration.py has to
    # know if the IP_COMMAND should come from a file or a command
    options, mode = arg_parser()

    if options.debug:
        print(f"The debug option was set.  Mode is {mode}", file=sys.stderr)
    # Get what the system currently actually is
    current_system: SystemDescription = SystemDescription.discover()
    try:
        if mode == constants.Modes.BOOT:
            current_system.test()
        elif mode == constants.Modes.DIAGNOSE:
            # This is the case where we want to compare the current state against the nominal state
            nominal_system: SystemDescription = SystemDescription.system_description_from_file(options.filename)
            current_system.diagnose(nominal_system)
        elif mode == constants.Modes.NOMINAL:
            current_system.nominal(options.filename)
        elif mode == constants.Modes.TEST:
            current_system.test()
        elif mode == constants.Modes.MONITOR:
            current_system.monitor()
        else:
            raise ValueError(f"Mode is {mode} but should be one of the constants in constants.Modes")
    except NotImplementedError as n:
        print(f"The mode you selected {str(mode)} isn't implemented yet {str(n)}", file=sys.stderr)

"""
        # We want to find out what the current state of the system is and record it in a file if
        # in NOMINAL mode or else display it if in BOOT mode
        applications: application.Application = application.Application()
        presentations = presentation.Presentation()
        sessions = session.Session()
        transports = transport.Transport()
        networks = network.Network()
        # Interface.discover() returns a dictionary keyed by device name and value is the MAC address
        interfaces_dict = interface.Interface.discover()

        # Compare the current configuration against a "nominal" configuration in the file and
        # note any changes
        (applications, presentations, sessions, transports, networks, interfaces) = \
            self.read_configuration(configuration_filename)
    elif mode != constants.Modes.NOMINAL:
        raise ValueError(f"mode is {str(mode)} but should be one of BOOT, CURRENT, NAMED, NOMINAL, or TEST")

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
    parser = argparse.ArgumentParser()
    print("BUG: add single letter options!", file=sys.stderr)
    parser.add_argument('--boot', help="Use at boot time.  Outputs messages color coded with status of network "
                                       "subsystems, and then exits", action="store_true", dest="boot")
    parser.add_argument('--monitor',
                        help="Use while system is running.  Presents a RESTful API that a client can use to "
                             "monitor the state of the network on a host", action="store_true", dest="monitor")
    parser.add_argument('--diagnose', help="Use when a problem is detected.", action="store_true", dest="diagnose")
    parser.add_argument('--test', help="Test a particular part of the network", action="store_true", dest="test")
    parser.add_argument('--nominal', help="Use when the system is working properly to capture the current state."
                                          "This state will serve as a reference for future testing",
                        action="store_true", dest="nominal")
    parser.add_argument('-p', '--port', type=int, default=constants.port,
                        help='Port where server listens when in monitor mode, default %s' % constants.port)
    parser.add_argument("--debug", default=False, action="store_true", dest="debug")
    options = parser.parse_args()

    # Select one and only one of these options
    # Look at the arg parser documentation, https://docs.python.org/3/library/argparse.html
    # There is a mechanism in there to make sure that one and only option is selected.
    if (options.boot + options.monitor + options.diagnose + options.test + options.nominal) != 1:
        raise ValueError(
            "Must have exactly one of --boot (or -b), --monitor (or -m), --diagnose (or -d), --nominal (or -N)\n"
            "sys.argv is " + str(sys.argv))
    if options.boot:
        mode = constants.Modes.BOOT
    elif options.diagnose:
        mode = constants.Modes.DIAGNOSE
    elif options.monitor:
        mode = constants.Modes.MONITOR
    elif options.test:
        mode = constants.Modes.TEST
    elif options.nominal:
        mode = constants.Modes.NOMINAL
    else:
        raise AssertionError("The arg_parser returned all mode options cleared.  options is " + str(options))
    return (options, mode)

    # As of 2018-07-29, there is a bug: the --debug option is not handled at all


if __name__ == "__main__":
    # Pass a length 0 list for production
    # Actually, here you'd never want to pass ANYTHING, because that's a job for pytest.
    main(["--boot", "--debug"], )
