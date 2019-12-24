#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
import socket
import sys
from time import sleep
from typing import List

import network
import utilities
from constants import ErrorLevels
from network import Network
from utilities import report

# These should come from a configuration file or a mock
BORDER_GATEWAY_4 = "96.120.102.161"
BORDER_GATEWAY_6 = "2001:558:4082:5c::1"


def main(stdscr: curses):
    stdscr.clear()
    print(f"The type of stdscr is {type(stdscr)}", file=sys.stderr)
    for family in [socket.AF_INET, socket.AF_INET6]:
        nw_obj: network.Network = network.Network(family=family)
        default_gateway: List = nw_obj.default_gateway
        assert isinstance(default_gateway, list), \
            f"{nw_obj.family_str} default_gateway should be a list, is actually {type(default_gateway)}."
        nw_obj.report_default_gateways_len()

def verify_ping(gw: str, nwobj: Network) -> None:
    severity: ErrorLevels = nwobj.ping(gw)
    utilities.report(f"Default {nwobj.family_str} gateway {gw} pingable: "
                     f"{ErrorLevels.__str__(severity)}", severity=severity)


if "__main__" == __name__:
    while True:
        curses.wrapper(main)
        sleep(1)
