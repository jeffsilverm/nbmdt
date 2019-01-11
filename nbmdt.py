#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#


# https://pypi.python.org/pypi/termcolor
import argparse
import json
import os
import platform
import sys
import typing
from typing import Tuple, List

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
mode = None


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
                 # Removed mode - it's not part of the system description, it's how nbmdt processes a system description
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
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"The file {filename} does not exist")
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
        result = "{0}\n{1}\n{2}\n{3}\n{4}\n{5}".format(str(self.applications), str(self.presentations),
                                                       str(self.sessions), str(self.transports), str(self.networks),
                                                       str(self.datalinks))
        return result

    def nominal(self, filename) -> None:
        print(f"The nominal configuration file is going to be {filename}", file=sys.stderr)
        self.file_from_system_description(filename)

    def boot(self) -> constants.ErrorLevels:
        print("Going to test in boot mode", file=sys.stderr)
        raise NotImplementedError

    def monitor(self, port) -> None:
        print(f"going to monitor on port {port}", file=sys.stderr)
        raise NotImplementedError

    def diagnose(self, filename )-> constants.ErrorLevels:
        print(f"In diagnostic mode, nomminal filename is {filename}", file=sys.stderr)
        nominal_system: SystemDescription = SystemDescription.system_description_from_file(filename)
        raise NotImplementedError
        return constants.ErrorLevels.UNKNOWN

    def test(self, test_specification) -> constants.ErrorLevels:
        print(f"The test_specification is {test_specification}", file=sys.stderr)
        raise NotImplementedError
        return constants.ErrorLevels.UNKNOWN


def main(args: List[str] = None):
    """
    Parse arguments, decide what mode to work in.
    :param args: a list of options,perhaps passed by a debugger.
    :return:
    """

    global options, mode

    # The caller might pass some arguments for testing purposes.  In this case, ignore the command line args
    if args is None:
        args = sys.argv[1:]
    assert "nbmdt" not in args, \
        f"'nbmdt' is in args and shouldn't be.  Probably due to a failure in a test frame.  args is {args} ."
    options, mode = arg_parser(args)
    assert type(options) == argparse.Namespace, \
        f"options should be of type argparse.Namespace but is actually {type(options)}"
    assert type(mode) == constants.Modes, f"mode should be of type constants.Modes but is actually {type(mode)}"

    if options.debug:
        print(f"The debug option was set.  Mode is {str(mode)} coded as {mode}", file=sys.stderr)
    # Get what the system currently actually is
    current_system: SystemDescription = SystemDescription.discover()
    try:
        if mode == constants.Modes.BOOT:
            current_system.boot()
        elif mode == constants.Modes.DIAGNOSE:
            # This is the case where we want to compare the current state against the nominal state
            if not hasattr(options, 'configuration_filename') or options.configuration_filename is None:
                raise ValueError(
                    "You did not specify a configuration filename when you asked nbmdt to diagnose a system")
            current_system.diagnose(options.configuration_filename)
        elif mode == constants.Modes.NOMINAL:
            current_system.nominal(options.configuration_filename)
        elif mode == constants.Modes.TEST:
            current_system.test(options.test_specification)
        elif mode == constants.Modes.MONITOR:
            current_system.monitor(options.monitor_port)
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


def arg_parser(args) -> Tuple:
    """
    Parse the command line parsed_options
    :rtype: argparse.Namespace
    :return: an object with all of the parsed_options included as attributes
    """

    # Issue 24 https://github.com/jeffsilverm/nbmdt/issues/24
    global parsed_options
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--boot', '-b', help="Use at boot time.  Outputs messages color coded with status of network "
                                            "subsystems, and then exits", action="store_const",
                       const=constants.Modes.BOOT, dest="boot")
    group.add_argument('--monitor', '-m',
                       help="Use while system is running.  Presents a RESTful API that a client can use to "
                            "monitor the state of the network on a host.  ",
                       action="store", type=int, dest="monitor_port")
    # Issue 27 https://github.com/jeffsilverm/nbmdt/issues/27
    group.add_argument('--diagnose', '-d',
                       help="Use when a problem is detected.  Compares the current state of the system "
                            "against a nominal state.  CONFIGURATION_FILE is optional, if not given"
                            "the diagnose tests the ability of the system to automatically configure itself",
                       nargs='?', default=None,
                       action="store", dest="configuration_filename")
    group.add_argument('--test', '-t', help="Test a particular part of the network", action="store",
                       dest="test_specification")
    group.add_argument('--nominal', '-N', help="Use when the system is working properly to capture the current state."
                                               "This state will serve as a reference for future testing.  "
                                               "CONFIGURATION_FILE is required", action="store",
                       dest="configuration_filename")
    parser.add_argument("--debug", default=False, action="store_true", dest="debug")

    try:
        parsed_options = parser.parse_args(args=args)
    except argparse.ArgumentError as a:
        print("argparse.ArgumentError was raised. args is " + str(args) + "exception is " + str(a), file=sys.stderr)
        # Hail Mary - no matter how bad the argument list is butchered, boot mode should still work
        parsed_options.boot = constants.Modes.BOOT
    except SystemExit as s:
        print(f"parser.parse_args raised a SystemExit error. Before I die, args is {args}"\
              f"and the exception information is {str(s)}")
        raise SystemExit(s)


    if parsed_options.boot is not None:
        mode = constants.Modes.BOOT
    elif parsed_options.configuration_filename is not None:
        mode = constants.Modes.DIAGNOSE
    elif parsed_options.test_specification is not None:
        mode = constants.Modes.TEST
    elif parsed_options.monitor_port is not None:
        mode = constants.Modes.MONITOR
    elif parsed_options.configuration_filename is not None:
        mode = constants.Modes.NOMINAL
    else:
        raise AssertionError(f"parsed_options did not have a way to set mode\n{dir(parsed_options)}")

    """# Select one and only one of these parsed_options
    # Look at the arg parser documentation, https://docs.python.org/3/library/argparse.html
    # There is a mechanism in there to make sure that one and only option is selected.
    if (parsed_options.boot + hasattr(parsed_options, "monitor") + hasattr(parsed_options, "diagnose") +
            parsed_options.test + parsed_options.nominal) != 1:
        raise ValueError(
            "Must have exactly one of --boot (or -b), --monitor (or -m), --diagnose (or -d), --nominal (or -N)\n"
            "sys.argv is " + str(sys.argv))
    if parsed_options.boot:
        mode = constants.Modes.BOOT
    elif hasattr(parsed_options, 'diagnose'):
        parsed_options.filename: str = parsed_options.diagnose
        mode = 
    elif parsed_options.monitor:
        mode = constants.Modes.MONITOR
    elif parsed_options.test:
        mode = constants.Modes.TEST
    elif hasattr(parsed_options, 'nominal'):
        mode = constants.Modes.NOMINAL
        parsed_options.filename: str = parsed_options.nominal
    else:
        raise AssertionError("The arg_parser returned all mode parsed_options cleared.  parsed_options is " + 
        str(parsed_options))
    """

    return parsed_options, mode

    # As of 2018-07-29, there is a bug: the --debug option is not handled at all


if __name__ == "__main__":
    main()
