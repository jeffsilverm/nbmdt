#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#
import argparse
import sys
from typing import Tuple, List

import constants
import utilities

# from physical import Physical
# import interface  # OSI layer 2: ethernet, WiFi       # issue 25
# import datalink  # OSI layer 2: # Media Access Control: arp, ndp
# import network  # OSI layer 3: IPv4, IPv6 should be called network, routing
# import physical  # OSI layer 1: Hardware: ethernet, WiFi, RS-232, etc.
# import presentation  # OSI layer 6:
# import session  # OSI layer 5:
# import transport  # OSI layer 4: TCP, UDP (and SCTP if it were a thing)

DEBUG = True
try:
    print("Testing the __file__ special variable: " + __file__, file=sys.stderr)
except Exception as e:  # if anything goes wrong
    print("Testing the __file__ special variable FAILED, exception is " + str(e), file=sys.stderr)
# Issue 29 moved the definitions of
# type_application_dict, type_presentation_dict, type_session_dict
# type_transport_dict, type_network_dict, type_datalink_dict, type_interface_dict
# To constants.py  Re-write Issue 25 to reflect this change
#
# try:
#    type_physical_dict = typing.Dict[str, physical.Physical]
# except AttributeError as e:
#    print(f"physical.Physical is raising an Attribute error.  {dir(physical)}",
#          f"physical is in file {physical.__file__} . ", file=sys.stderr)

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
    # Issue 29 https://github.com/jeffsilverm/nbmdt/issues/29
    current_system: utilities.SystemDescription = utilities.SystemDescription.discover()
    if options.debug and current_system.applications["applications"] != "Mocked":
        print("""WARNING: debugging and current_system.applications["applications"] != "Mocked" """, file=sys.stderr)
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

    current_system = utilities.SystemDescription(mode=mode)
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
# Issue 29 https://github.com/jeffsilverm/nbmdt/issues/29
    nominal_system_description = utilities.SystemDescription ( configuration_file="nominal.txt" )
    current_system_description = utilities.SystemDescription ( )
    
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
        print(f"parser.parse_args raised a SystemExit error. Before I die, args is {args}" 
              f"and the exception information is {str(s)}")
        raise SystemExit(s)

    if parsed_options.boot is not None:
        mode_ = constants.Modes.BOOT
    elif parsed_options.configuration_filename is not None:
        mode_ = constants.Modes.DIAGNOSE
    elif parsed_options.test_specification is not None:
        mode_ = constants.Modes.TEST
    elif parsed_options.monitor_port is not None:
        mode_ = constants.Modes.MONITOR
    elif parsed_options.configuration_filename is not None:
        mode_ = constants.Modes.NOMINAL
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

    return parsed_options, mode_

    # As of 2018-07-29, there is a bug: the --debug option is not handled at all


if __name__ == "__main__":
    main()
