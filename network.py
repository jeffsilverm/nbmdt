#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module is responsible for representing the routing tables.  There are at least 2: one for IPv4 and one for IPv6
import re
import socket
import subprocess
import sys
from typing import List, Dict, Tuple, Union

import utilities
from configuration import Configuration
from constants import ErrorLevels
from layer import Layer
from termcolor import cprint

# The color names described in https://pypi.python.org/pypi/termcolor are:
# Text colors: grey, red, green, yellow, blue, magenta, cyan, white
# Text highlights: on_grey, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white

# Issue #42 https://github.com/jeffsilverm/nbmdt/issues/42

IP_COMMAND = Configuration.find_executable('ip')
PING_COMMAND = Configuration.find_executable('ping')
# PING6_COMMAND = Configuration.find_executable('ping6')
cprint(f"Debugging network.py: {IP_COMMAND}, {PING_COMMAND}", 'green', file=sys.stderr)


class NotPingable(Exception):
    def __init__(self, name: str = None) -> None:
        cprint(f"{name} is not pingable", 'yellow', file=sys.stderr)

    pass


class Network(Layer):

    def __init__(self, family):
        """

        :rtype: Network: This is something of a placeholder, so if I write
        something common to both IPv4 and IPv6, it can go here.
        """

        super().__init__()
        if socket.AF_INET == family:
            self.family_flag = "-4"
            self.family_str = "IPv4"
        elif socket.AF_INET6 == family:
            self.family_flag = "-6"
            self.family_str = "IPv6"
        else:
            raise ValueError(
                f"family should be either {socket.AF_INET} (socket.AF_INET) or {socket.AF_INET6} (socket.AF_INET6"
                f"But it's actually {family}")
        self.family = family
        self.layer = Layer()
        # As part of issue 44, add the default_interface to this tuple
        rt: Tuple[List[Dict[str, str]], List, List] = self.parse_ip_route_list_cmd()
        (self.routing_table, self.default_gateway, self.default_dev) = rt
        # Issue 44
        assert self.default_dev != ['dev'], f"default_dev is ['dev'] and that's wrong"

    @property
    def get_default_gateway(self):
        return self.routing_table[1]

    def get_status(self) -> ErrorLevels:
        return self.layer.get_status()

    pass

    # Issue 44 - add a list of default devices in addition to the list of default addresses
    def parse_ip_route_list_cmd(self) -> Tuple[List[Dict[str, str]], List, List]:
        """
        This method runs the ip route list command and parses the output
        It's here because the output of the ip -4 route list command and the
        ip -6 route list command are very similar
        :return a list of routes.  Each route is a dictionary of the fields of a route
                            in the routing table
        """

        # https://docs.python.org/3/library/subprocess.html
        cpi = subprocess.run(args=[IP_COMMAND, self.family_flag, 'route', 'list'],
                             stdin=None,
                             input=None,
                             stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None,
                             check=False, encoding="utf-8", errors=None)
        if cpi.returncode != 0:
            raise subprocess.CalledProcessError
        # Because subprocess.run was called with encoding=utf-8, output will be a string
        results = cpi.stdout
        lines = results.split('\n')[:-1]  # Don't use the last element, which is empty
        """
jeffs@jeffs-desktop:~/nbmdt (blue-sky)*$ ip -4 route
default via 192.168.0.1 dev eno1 proto static metric 100 
10.0.3.0/24 dev lxcbr0 proto kernel scope link src 10.0.3.1 linkdown 
169.254.0.0/16 dev eno1 scope link metric 1000 
192.168.0.0/24 dev eno1 proto kernel scope link src 192.168.0.16 metric 100 
192.168.122.0/24 dev virbr0 proto kernel scope link src 192.168.122.1 linkdown 
jeffs@jeffs-desktop:~/nbmdt (blue-sky)*$ 
"""
        """
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (dev_0) *  $ ip -6 route list
::1 dev lo proto kernel metric 256 pref medium
2601:602:8500:145::/64 via fe80::c256:27ff:feca:724 dev wlx000e8e06e1a7 proto ra metric 600 pref high
fdda:cfd2:28e3::/64 dev enp3s0 proto kernel metric 100 pref medium
fe80::/64 dev enp3s0 proto kernel metric 100 pref medium
fe80::/64 dev flannel.1 proto kernel metric 256 pref medium
fe80::/64 dev wlx000e8e06e1a7 proto kernel metric 600 pref medium
default via fdda:cfd2:28e3::1 dev enp3s0 proto static metric 20100 pref medium
default via fe80::c256:27ff:feca:724 dev wlx000e8e06e1a7 proto ra metric 20600 pref medium
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (dev_0) *  $ 
        """
        route_list = list()
        # It is possible, but unlikely, that there is more than one default gateway
        # That would be a misconfiguration
        default_gateway = []
        default_dev = []
        for line in lines:  # lines is the output of the ip route list command
            fields = line.split()
            route = dict()  # route is a description of a route.  It is keyed by the name of a field in the output
            # of the ip route.  The first field is an address/subnet mask combination, so handle it
            # specially
            if fields[0] == "default":
                if self.family == socket.AF_INET:
                    (network, mask) = ("0.0.0.0", "0")
                else:
                    (network, mask) = ("::", "0")
                default_gateway.append(fields[2])
                default_dev.append(fields[3])
            else:
                try:
                    (network, mask) = fields[0].split("/")
                except ValueError:
                    print(f"fields[0] is {fields[0]} and does not contain a '/'", file=sys.stderr)
                    (network, mask) = (fields[0], None)
            route['destination'] = (network, mask)

            # fields[1] is a special case
            if fields[1] == "via":
                assert fields[3] == 'dev', "Parse error in parse_ip_route_list_cmd:" \
                                           f"fields[3] should be 'dev' but is actually {fields[3]}."
                route["gateway"] = fields[2]
                route["device"] = fields[4]
            elif fields[1] == "dev":
                route["gateway"] = ""  # Not really a route, but rather a
                # marker to the kernel to tell which device these packets should go to
                route["device"] = fields[2]
            else:
                raise AssertionError(f"fields[1] can be 'via' or 'dev' but it's actually {fields[1]}")

            for i in range(3, len(fields) - 1, 2):
                if fields[i] == "linkdown":
                    route["linkdown"] = True
                    # linkdown is a flag, not the title of a field.  No value follows it
                    break
                route[fields[i]] = fields[i + 1]
            route_list.append(route)
        return route_list, default_gateway, default_dev

    # Issue 43 - https://github.com/jeffsilverm/nbmdt/issues/43  Return constants.ErrorLevels, not a tuple
    def ping(self, address: Union[List, str], count: str = "10", min_for_good: int = 8, slow_ms: float = 100.0,
             production=True) -> ErrorLevels:
        """
        This does a ping test of the machine with this IPv4 or IPv6 address
        :param  address            the remote machine to ping
        :param  min_for_good     The minimum number of successful pings required for the machine to be up
        :param  count           number of packets to be sent, default is 10
        :param  min_for_good    the number of packets that must be returned in order to consider the remote machine "up"
        :param  slow_ms         The maximum amount of time, in milliseconds, that is allowed to transpire before the
                                remote machine will be considered "slow"
        :param  production      If production is false, then ping4 won't raise a NotPingable exception
        :return     NORMAL if pingable and fast enough, SLOW if round trip time (RTT) is too slow, DOWN if not pingable,
                    DOWN_DEPENDENCY if down because of a DNS failure (not implemented as of 21-Dec-2019)
        """
        if isinstance(address, list) and len(address) == 1:
            address = address[0]
        assert isinstance(address, str), "address should be a str or a list of "
        "length 1 but it's actually a {type(address)} length={len(address)}."

        # Issue 11 starts here https://github.com/jeffsilverm/nbmdt/issues/11
        # -c is for linux, use -n for windows.
        # https://github.com/jeffsilverm/nbmdt/issues/44
        # This is complicated, and it needs to be complicated for IPv6 because
        # IPv4 doesn't need to know the interface.
        if self.family == socket.AF_INET6:
            # Is this a Globally Unique Address?  It is if the MSB 3 bits are 001
            for ent in self.routing_table:
                # Issue 44
                # This is naive.  I should use some sort of membership test.
                if ent['destination'] == address:
                    default_dev = ent["device"]
                    break
            else:
                self.dump_network_obj()
                raise AssertionError(f"default_dev not found.  Address is {address}")
            args = [PING_COMMAND, self.family_flag, '-c', count, '-I', default_dev, address]
        else:
            args = [PING_COMMAND, self.family_flag, '-c', count, address]
        cpi = subprocess.run(args=args,
                             stdin=None,
                             input=None,
                             stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None,
                             check=False, encoding="utf-8", errors=None)
        # return status = 0 if everything is okay
        # return status = 2 if DNS fails to look up the name
        # return status = 1 if the device is not pingable
        if cpi.returncode == 2:
            raise utilities.DNSFailure(name=address, query_type=('A' if self.family == socket.AF_INET else 'AAAA'))
        elif cpi.returncode != 0 and cpi.returncode != 1:
            cprint(
                f"About to raise a subprocess.CalledProcessError exception. name={address} cpi={cpi} returncode is "
                f"{cpi.returncode}",
                'red', file=sys.stderr)
            raise subprocess.CalledProcessError
        elif cpi.returncode == 1 and production:
            raise NotPingable(name=address)
        else:
            # Because subprocess.run was called with encoding=utf-8, output will be a string
            results = cpi.stdout
            lines = results.split('\n')[:-1]
            # Don't use the last element, which is empty
            """
jeffs@jeffs-laptop:~/nbmdt (development)*$ ping -c 4  f5.com
PING f5.com (104.219.110.168) 56(84) bytes of data.
64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=1 ttl=249 time=24.0 ms
64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=2 ttl=249 time=23.8 ms
64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=3 ttl=249 time=23.3 ms
64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=4 ttl=249 time=46.3 ms

--- f5.com ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3003ms
rtt min/avg/max/mdev = 23.326/29.399/46.300/9.762 ms
jeffs@jeffs-laptop:~/nbmdt (development)*$ 
            """
            # Failsafe initialization
            # slow: bool = True
            # up: bool = cpi.returncode == 0
            # loop through output of ping command
            for line in lines:
                if "transmitted" in line:
                    # re.findall returns a list of length 1 because there is 1 match to the RE
                    packet_counters = \
                        re.findall("""(\d+).*?(\d+).*received.*(\d+).*(\d+)""", line)[0]  # noqa
                    # packets_xmit = packet_counters[0]
                    packets_rcvd = packet_counters[1]
                    # If at least one packet was received, then the remote machine
                    # is pingable and the NotPingable exception will not be raised
                    if packets_rcvd == count:
                        results = ErrorLevels.NORMAL
                    elif int(packets_rcvd) >= min_for_good:
                        results = ErrorLevels.DEGRADED
                    else:
                        results = ErrorLevels.DOWN
                elif "rtt " == line[0:4]:  # crude, I will do something better, later
                    # >>> re.findall("\d+\.\d+", "rtt min/avg/max/mdev = 23.326/29.399/46.300/9.762 ms")
                    # ['23.326', '29.399', '46.300', '9.762']
                    # >>>
                    # The RE matches a fixed point number, and there are 4 of them.  The second one is the average
                    numbers = re.findall("""\d+\.\d+""", line)  # noqa
                    slow = float(numbers[1]) > slow_ms
                    if results == ErrorLevels.NORMAL and slow:
                        results = ErrorLevels.SLOW
                else:
                    pass
            return results

    def __str__(self):
        """This method produces a nice string representation of a routing table"""
        for w in self.routing_table:
            return f"dest={w.get('destination')} {w.get('gateway')} " \
                   f"dev={w.get('dev')} " \
                   f"metric={w.get('metric')} proto={w.get('proto')} " \
                   f"src={w.get('src')} scope={w.get('scope')} " + \
                   ("linkdown" if w.get('linkdown', True) else "linkUP")

    def report_default_gateways_len(self) -> None:
        """
        This is common for IPv4 and IPv6

        """
        num_def_gateways = len(self.default_gateway)
        # The assumption is that you *must* have a default gateway (that's not strictly true, but it is for all
        # non-strange
        # use cases).
        # You *might* have more than one default gateway, but that's probably a configuration error
        # You *should* have one and only one default gateway
        if num_def_gateways == 1:
            utilities.report(f"Found default {self.family_str} gateway", severity=ErrorLevels.NORMAL)
        elif num_def_gateways > 1:
            utilities.report(f"Found multiple default {self.family_str} gateways", severity=ErrorLevels.OTHER)
        elif num_def_gateways == 0:
            utilities.report(f"Found NO default {self.family_str} gateways", severity=ErrorLevels.DOWN)

    def dump_network_obj(self):
        """This a "hail mary" move: dump the entire object"""
        print(self, file=sys.stderr)  # dump the routing table
        print("Default gateways are" + str(self.default_gateway), file=sys.stderr)
        print("Default devices are" + str(self.default_dev), file=sys.stderr)
        print("Family is ", self.family_str, self.family_flag, self.family, file=sys.stderr)
        print("Layer is ", self.layer, file=sys.stderr)


if __name__ in "__main__":

    ipv4_routing_table = Network(socket.AF_INET)
    ipv6_routing_table = Network(socket.AF_INET6)
    print(40 * "=")
    for r in ipv4_routing_table.routing_table:
        print(r.__str__())
        print(f"The gateway is {ipv4_routing_table.default_gateway}\n")
    print(40 * "=")
    for r in ipv6_routing_table.routing_table:
        print(r.__str__())
        print(f"The gateway is {ipv6_routing_table.default_gateway}\n")
    print(40 * "-")
    inet_dgw = ipv4_routing_table.default_gateway[0]
    print(
        f"The default IPv4 gateway {inet_dgw} is "
        f"{('' if ipv4_routing_table.ping(inet_dgw, production=False) else 'NOT')} pingable")
    for t in ["208.97.189.29", "Commercialventvac.com", "ps558161.dreamhost.com", 'google.com']:
        print(f"{t} is {('' if ipv4_routing_table.ping(t, production=False) else 'NOT')} pingable")
    print(40 * ".")
    inet6_dgw = ipv6_routing_table.default_gateway[0]
    print(
        f"The default IPv6 gateway {inet6_dgw} is "
        f"{('' if ipv6_routing_table.ping(inet6_dgw, production=False) else 'NOT')} pingable")
    for t in ["2607:f298:5:115f::23:e397", "Commercialventvac.com", "ps558161.dreamhost.com", 'google.com']:
        try:
            print(f"{t} is {('' if ipv6_routing_table.ping(t, production=False) else 'NOT')} pingable")
        except utilities.DNSFailure as u:
            cprint(f"There was a DNS failure exception {str(u)} on {t}.  Continuing")
    print(40 * "-")
