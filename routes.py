#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module is responsible for representing the routing tables.  There are at least 2: one for IPv4 and one for IPv6
import ipaddress  # https://docs.python.org/3/library/ipaddress.html?highlight=ipaddress#module-ipaddress
import pprint
import socket
import subprocess
import sys
import typing
from typing import Any
import os

# import application
# import configuration
# from utilities import OsCliInter
# import utilities
# from layer import Layer

DEBUG = True


# IP_COMMAND="/sbin/ip"  in network.py


class IPRoute(object):
    """
    A lot of functionality between IPv4 and IPv6 is the same.  So the version agnostic code goes here, and the
    version not-so-agnostic code goes in classes that inherit from this class.
    """

    # These keywords come from the ip-route man page, https://www.man7.org/linux/man-pages/man8/ip-route.8.html
    TYPE = {"unicast", "local", "broadcast", "multicast", "throw", "unreachable", "prohibit", "blackhole", "nat"}
    FAMILY = {"inet", "inet6", "mpls", "bridge", "link"}
    IP_COMMAND_FIELD_NAMES = {"to", "tos", "dsfield", "metric", "preference", "table", "vrf", "dev", "via", "src",
                              "realm", "mtu", "window", "rtt", "rttvar", "rtt_min"}  # There are more words!
    ENCAPTYPE = {"mpls", "ip", "bpf", "seg6", "seg6local", "ioam6", "xfrm"}
    IP_COMMAND_FIELD_OPTIONALS = {"to": TYPE, "via": FAMILY, "encap": ENCAPTYPE, "mtu": {"lock"}}

    def __init__(self) -> None:

        self.ip4_routing_table = self.discover(socket.AF_INET)
        self.ip6_routing_table = self.discover(socket.AF_INET6)

    """ Returns a dictionary of routes, key'd by destination.  Each route is represented by a dictionary of
    fields from the route command.
    """

    @classmethod
    def discover(cls, family: socket.AddressFamily) -> typing.Dict:  # IPRoute
        """discover returns a list of routes, for either IPv4 or IPv6.  Each route is a dictionary keyed by
        fields from the ip command.
        """
        route_dict = {}

        def handle_default() -> None:
            """Handle the special case of a default route, which is designated by the word 'default'

            There is a known problem: there can be more than one default route.  In that case, pick the
            default with the **lowest** metric or preference.
            """
            print("INFORMATION: There is a known problem with multiple default routes.", file=sys.stderr)

            # Create numeric synonyms for the default gateway;
            if family == socket.AF_INET:
                default_synonym = "0.0.0.0/0"
            elif family == socket.AF_INET6:
                default_synonym = "::/0"
            else:
                raise NotImplementedError("Unknown family '%s'" % family)

            if "default" in route_dict and default_synonym not in route_dict:
                route_dict[default_synonym] = route_dict["default"]
            elif default_synonym in route_dict and "default" not in route_dict:
                route_dict["default"] = route_dict[default_synonym]
            elif "default" not in route_dict and default_synonym not in route_dict:
                print(f"WARNING: no default route for {family}", file=sys.stderr)
            else:
                pass  # no need to do anything, the synonym already exists
            if "ADDRESS" not in route_dict["default"]:
                # Strict is True here because if this constructor call fails, it means I made a
                route_dict["default"]["ADDRESS"] = ipaddress.ip_network(default_synonym, strict=True)
            assert "ADDRESS" in route_dict[default_synonym], f'There is no key ADDRESS in route_dict[default_synonym], it is {route_dict[default_synonym]}. '
            assert str(route_dict["default"]["ADDRESS"]) == default_synonym, f'route_dict["default"]["ADDRESS"] should be {default_synonym} but is {route_dict["default"]["ADDRESS"]}'
            assert str(route_dict[default_synonym]["ADDRESS"]) == default_synonym, f'route_dict[default_synonym]["ADDRESS"] should be {default_synonym} but is {route_dict[default_synonym]["ADDRESS"]}'




        def run_ip_route_command(family: socket.AddressFamily) -> str:
            """
            Run the ip route command and return the output as a string.
            :rtype: str
            """
            output__str = None
            if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
                if "pytest" in sys.modules != "PYTEST_CURRENT_TEST":
                    print("WARNING: 'pytest' in sys.modules != 'PYTEST_CURRENT_TEST' in os.environ.  " +
                          f"'pytest' in sys.modules is {'pytest' in sys.modules}, 'PYTEST_CURRENT_TEST' in os.environ "+
                          f"is {'PYTEST_CURRENT_TEST' in os.environ}", file = sys.stderr)
                    raise NotImplementedError(
                        f"run_ip_route_command I assume is patched by pytest in test_routes.py! {family}")
            else:
                if family == socket.AF_INET:
                    family_str = "inet"
                elif family == socket.AF_INET6:
                    family_str = "inet6"
                else:
                    raise ValueError(
                        f"Invalid value for family: {family}.  This is a software error, please submit an SPR")
                # This is the recommended approach for running an external command in python 3.5 and later.
                # From https://docs.python.org/3/library/subprocess.html
                completed: subprocess.CompletedProcess = subprocess.run(
                    ["/sbin/ip", "--family", family_str, "route", "show"],
                    capture_output=True,
                    # if capture_output is false (the default), then stdout and stderr will not be captured
                    stdin=None, input=None, stdout=None, stderr=None, shell=False, timeout=None,
                    check=False, encoding="utf-8", text=True,
                    errors=None)
                if completed.returncode != 0:
                    raise subprocess.CalledProcessError()
                output__str: str = str(completed.stdout)

            return output__str

        output_str = run_ip_route_command(family=family)

        try:
            for r in output_str.split("\n"):
                if len(r) == 0:
                    continue
                # The next() function expects an interator.  A list is *not* an iterator, it does not have a __next__() method
                # However, iter() will explicitly convert a list into an interator and that *does* have a __next__() function
                words: typing.Iterator[str] = iter(r.split())
                destination_str: str = next(words)
                route_dict[destination_str] = dict()
                for word in words:
                    field_name = word
                    if field_name in cls.IP_COMMAND_FIELD_OPTIONALS:
                        maybe_field_name = next(words)
                        if maybe_field_name in cls.IP_COMMAND_FIELD_OPTIONALS[field_name]:
                            value = next(words)
                            value = (maybe_field_name, value)
                        else:
                            value = (maybe_field_name,)  # force value to be a tuple
                        route_dict[destination_str][field_name] = value
                    else:
                        route_dict[destination_str][field_name] = next(words)
                if destination_str == "default":
                    continue
                try:
                    route_dict[destination_str]["ADDRESS"] = ipaddress.ip_network(destination_str)
                except ValueError as v:
                    print(f"WARNING: bad destination address '{destination_str}' raised a ValueError exception {v}",
                          file=sys.stderr)
                    route_dict[destination_str]["ADDRESS"] = ipaddress.ip_network(destination_str, strict=False)
                    print(f"INFORMATION: Continuing.  IP address us {route_dict[destination_str][ADDRESS]}.", file=sys.stderr)

        except StopIteration:
            print(f"WARNING: The StopIteration exception was raised.  That should not happen, not here. r={r}", file=sys.stderr)

        # Handle special cases
        handle_default()

        assert "ADDRESS" in route_dict["default"], f"The default route entry in the route_dict does not contain a 'ADDRESS' key. {route_dict}"


        # From https://stackoverflow.com/questions/10259266/what-does-proto-kernel-means-in-unix-routing-table
        # allowed values of proto are redirect, kernel, boot, static, and ra

        return route_dict



if "__main__" == __name__:
    ipv4_route_table = IPRoute.discover(family=socket.AF_INET)
    ipv6_route_table = IPRoute.discover(family=socket.AF_INET6)
    pprint.pp(ipv4_route_table)
    pprint.pp(ipv6_route_table)
