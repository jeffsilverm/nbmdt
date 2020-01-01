#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# import curses
import socket
from time import sleep
from typing import List

import network
import utilities
from constants import ErrorLevels
import ansiescapes

# These should come from a configuration file or a mock
BORDER_GATEWAY_4 = "96.120.102.161"
BORDER_GATEWAY_6 = "2001:558:4082:5c::1"


def main():
    nw_obj = dict()
    for family in [socket.AF_INET, socket.AF_INET6]:
        nw_obj[family]: network.Network = network.Network(family=family)
        default_gateway: List = nw_obj[family].default_gateway
        assert isinstance(default_gateway, list), \
            f"{nw_obj[family].family_str} default_gateway should be a list, is actually {type(default_gateway)}."
        nw_obj[family].report_default_gateways_len()
        # Issue 45
        for defgw in default_gateway:
            severity: ErrorLevels = nw_obj[family].ping(address=defgw)
            utilities.report(f"Default {nw_obj[family].family_str} gateway {str(defgw)} pingable: "
                             f"{ErrorLevels.__str__(severity)}", severity=severity)


if "__main__" == __name__:
    while True:
        print(ansiescapes.eraseScreen+ansiescapes.cursorTo(0,0))
        main()
        sleep(5)
