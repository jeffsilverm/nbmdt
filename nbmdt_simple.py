#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# From jeffs-windows-laptop

import curses
from typing import List

import network
import utilities
from utilities import report
from network import Network
from time import sleep
import socket
from constants import ErrorLevels


INET = "-4"
INET6 = "-6"

BORDER_GATEWAY_4 = "96.120.102.161"
BORDER_GATEWAY_6 = "2001:558:4082:5c::1"

network_obj_4: Network = network.Network(family=socket.AF_INET)
network_obj_6: Network = network.Network(family=socket.AF_INET6)




def main():

    for family in [ socket.AF_INET, socket.AF_INET6]:
        nw_obj: network.Network = network.Network(family=family)
        default_gateway: list = nw_obj.default_gateway
        assert isinstance(default_gateway, list), \
        f"default_gateway_4 should be a list, is actually {type(default_gateway)}."
        ldr = len(default_gateway)
    # The assumption is that you *must* have a default gateway (that's not strictly true, but it is for all non-strange
    # use cases).
    # You *might* have more than one default gateway, but that's probably a configuration error
    # You *should* have one and only one default gateway
        utilities.report("Default IPv4 gateway",
           severity=(ErrorLevels.NORMAL if ldr == 1 else (ErrorLevels.OTHER if ldr > 1 else ErrorLevels.DOWN)))
        if ldr > 0:
            for dg in default_gateway:
                verify_ping: ErrorLevels = nw_obj.ping(address=dg)
                report(condition=f"{nw_obj.family_str} default gateway {dg} ping: ", severity=verify_ping)
        else:
            report(condition=f"NO DEFAULT {nw_obj.family_str} GATEWAY", severity=ErrorLevels.DOWN)


def verify_ping(gw: str, nwobj: Network) -> None:
    severity: ErrorLevels = nwobj.ping(gw)
    utilities.report(f"Default {nwobj.family_str} gateway {gw} pingable: "
                     f"{ErrorLevels.__str__(severity)}", severity=severity)


if "__main__" == __name__:
    while True:
        curses.wrapper(main)
        sleep(10)
