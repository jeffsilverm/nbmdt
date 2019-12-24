#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# From jeffs-windows-laptop

import curses
import socket
from time import sleep
from typing import List

import network
import utilities
from constants import ErrorLevels
from network import Network

INET = "-4"
INET6 = "-6"

BORDER_GATEWAY_4 = "96.120.102.161"
BORDER_GATEWAY_6 = "2001:558:4082:5c::1"

network_obj_4: Network = network.Network(family=socket.AF_INET)
network_obj_6: Network = network.Network(family=socket.AF_INET6)


def report_default_gateways_len(num_def_gateways: int, family_str: str = "IPv4") -> None:
    """
    This is common for IPv4 and IPv6
    :param  num_def_gateways    number of default gateways
    :param  family_str  Either the string "IPv4" or "IPv6"
    """
    assert family_str == "IPv4" or family_str == "IPv6", f"family_str is {family_str}, should be either 'IPv4' or " \
                                                         f"'IPv6'"
    if num_def_gateways == 1:
        utilities.report(f"Found default {family_str} gateway", severity=ErrorLevels.NORMAL)
    elif num_def_gateways > 1:
        utilities.report(f"Found multiple default {family_str} gateways", severity=ErrorLevels.OTHER)
    elif num_def_gateways == 0:
        utilities.report(f"Found NO default {family_str} gateways", severity=ErrorLevels.DOWN)


def main():
    default_gateway_4: list = network_obj_4.default_gateway
    assert isinstance(default_gateway_4, list), \
        f"default_gateway_4 should be a list, is actually {type(default_gateway_4)}."
    ldr4 = len(default_gateway_4)
    default_gateway_6: List = network_obj_6.default_gateway
    assert isinstance(default_gateway_6, list), \
        f"default_gateway_6 should be a list, is actually {type(default_gateway_6)}."
    ldr6 = len(default_gateway_6)
    report_default_gateways_len(ldr4, "IPv4")
    report_default_gateways_len(ldr6, "IPv6")

    # The ping methods return a tuple: first element is True if pingable, second element is true
    # if response time (RTT) is acceptable.  What is "acceptable" can be specified in the method
    # call.  The defaults are reasonable.
    for gw in default_gateway_4:
        verify_ping(gw=gw, nwobj=network_obj_4)
    for gw in default_gateway_6:
        verify_ping(gw=gw, nwobj=network_obj_6)


def verify_ping(gw: str, nwobj: Network) -> None:
    severity: ErrorLevels = nwobj.ping(gw)
    utilities.report(f"Default {nwobj.family_str} gateway {gw} pingable "
                     f"{ErrorLevels.__str__(severity)}", severity=severity)


if "__main__" == __name__:
    while True:
        curses.wrapper(main)
        sleep(10)
