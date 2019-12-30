#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#
# https://pypi.python.org/pypi/termcolor
import argparse
import sys
import typing
from typing import Tuple
import json
import platform

import application  # OSI layer 7: HTTP, HTTPS, DNS, NTP
import constants
from constants import ErrorLevels
import interface  # OSI layer 1: ethernet, WiFi
import mac  # OSI layer 2: # Media Access Control: arp, ndp
import network  # OSI layer 3: IPv4, IPv6 should be called network
import transport  # OSI layer 4: TCP, UDP (and SCTP if it were a thing)
import session  # OSI layer 5:
import presentation  # OSI layer 6:
import utilities
import socket


DEBUG = True


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


if "__main__" == __name__ :
    routes = dict()
    default_routes = dict()
    for family in (socket.AF_INET, socket.AF_INET6 ):
        name = "IPv4" if family == socket.AF_INET else "IPv6"
        routes[family] : network.Network = network.Network.get_routes(family)
        default_routes[family] = network.get_default_routes(routes, family)
        if len(default_routes[family] == 1):
            utilities.report(f"Have a default {name} gateway", ErrorLevels.NORMAL)
        elif len(default_routes) > 1:
            utilities.report(f"There are {len(default_routes)} default {name} gateways!!",  ErrorLevels.OTHER)
        else:
            utilities.report(f"There is no default {name} gateway!", ErrorLevels.DOWN)
        def_gw = default_routes[family].gateway
        if network.ping( target=def_gw, family=family ):
            utilities.report(f"The default gateway for {name}, {def_gw}, is pingable", ErrorLevels.NORMAL)
        else:
            utilities.report(f"The default gateway for {name}, {def_gw}, is pingable", ErrorLevels.DOWN)




