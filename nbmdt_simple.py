#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from time import sleep
from typing import List

import network

INET = "-4"
INET6 = "-6"

BORDER_GATEWAY_4 = "96.120.102.161"
BORDER_GATEWAY_6 = "2001:558:4082:5c::1"

network_obj = network.Network()


def main():
    default_gateway_4: List[network.IPv4Address] = network.IPv4Route.get_default_ipv4_gateway()
    assert isinstance(default_gateway_4, list), \
        f"default_gateway_4 should be a list, is actually {type(default_gateway_4)}."
    ldr4 = len(default_gateway_4)
    report("Found default IPv4 gateway", green=(ldr4 == 1), red=(ldr4 == 0), yellow=(ldr4 > 1))
    default_gateway_6: List[network.IPv6Address] = network.IPv6Route.get_default_ipv6_gateway()
    assert isinstance(default_gateway_4, list), \
        f"default_gateway_4 should be a list, is actually {type(default_gateway_4)}."
    ldr6 = len(default_gateway_6)
    report("Found default IPv6 gateway", green=(ldr6 == 1), red=(ldr6 == 0), yellow=(ldr6 > 1))
    verify_ping_4 = network.IPv4Address.ping4(default_gateway_4[0])
    report("IPv4 default gateway pingable", green=(verify_ping_4 == 1.0),
           yellow=(verify_ping_4 < 1.0 and verify_ping_4 > 0.0), red=(verify_ping_4 == 0.0))
    verify_ping_6 = network.IPv6Address.ping6(default_gateway_6[0])
    report("IPv6 default gateway pingable", green=(verify_ping_6 == 1.0),
           yellow=(verify_ping_6 < 1.0 and verify_ping_4 > 0.0), red=(verify_ping_4 == 0.0))


def report(explanation, yellow=False, green=False, red=False):
    """
    Generate a report of the last verification (not test, test is reserved for pytest)
    :param explanation:
    :param red: True if utter failure
    :param yellow: True if merely wrong
    :param green: True if everything is okay
    :return:
    """
    status = ("RED" if red else ("YELLOW" if yellow else ("GREEN" if green else "UNKNOWN")))
    print(explanation + ": " + status)


if "__main__" == __name__:
    while True:
        main()
        sleep(10)
