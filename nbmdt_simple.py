#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# From jeffs-windows-laptop


import network
from time import sleep
import socket
from constants import ErrorLevels
from utilities import report


INET = "-4"
INET6 = "-6"

BORDER_GATEWAY_4 = "96.120.102.161"
BORDER_GATEWAY_6 = "2001:558:4082:5c::1"


def main():
    ipv4_routing_table: network.Network = network.Network(socket.AF_INET)
    ipv6_routing_table: network.Network = network.Network(socket.AF_INET6)
    ipv4_default_gateway = ipv4_routing_table.default_gateway
    ipv6_default_gateway = ipv6_routing_table.default_gateway
    ldr4 = len(ipv4_default_gateway)
    ldr6 = len(ipv6_default_gateway)
    # The assumption is that you *must* have a default gateway (that's not strictly true, but it is for all non-strange
    # use cases).
    # You *might* have more than one default gateway, but that's probably a configuration error
    # You *should* have one and only one default gateway
    report("Default IPv4 gateway",
           severity=(ErrorLevels.NORMAL if ldr4 == 1 else (ErrorLevels.OTHER if ldr4 > 1 else ErrorLevels.DOWN)))
    if ldr4 > 0:
        for dg in ipv4_default_gateway:
            verify_ping_4: ErrorLevels = ipv4_routing_table.ping(address=dg)
            report(condition=f"IPv4 default gateway {dg} ping: ", severity=verify_ping_4)
        else:
            report(condition="NO DEFAULT IPv4 GATEWAY", severity=ErrorLevels.DOWN)

    report("Default IPv6 gateway",
           severity=(ErrorLevels.NORMAL if ldr6 == 1 else (ErrorLevels.OTHER if ldr6 > 1 else ErrorLevels.DOWN)))
    if ldr6 > 0:
        for dg in ipv6_default_gateway:
            verify_ping_6: ErrorLevels = ipv6_routing_table.ping(address=dg)
            report(condition=f"IPv4 default gateway {dg} ping: ", severity=verify_ping_6)
        else:
            report(condition="NO DEFAULT IPv4 GATEWAY", severity=ErrorLevels.DOWN)


if "__main__" == __name__:
    while True:
        main()
        sleep(10)
