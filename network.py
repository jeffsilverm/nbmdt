#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module is responsible for representing the routing tables.  There are at least 2: one for IPv4 and one for IPv6
import utilities
import ipaddress
import re
import socket
import subprocess
import sys
from typing import List, Dict, Tuple, Union

from configuration import Configuration
from constants import ErrorLevels
from layer import Layer
from termcolor import cprint
from utilities import OsCliInter as Os



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
        # The rationale for this Rube Goldberg two step is that you can't do type
        # conformance testing when breaking a tuple into fields.
        rt: Tuple[List[Dict[ipaddress]], List, List] = self.parse_ip_route_list_cmd
        self.route_list, self.dgw, self.default_dev = rt    # dgw is Default GateWay
        """
        # Moved to test_network.py
        
        assert isinstance(rt[1], list), \
            f"rt[1] should be a list of ipaddress but is {type(rt[1])}."

        for e in rt[0]:
            assert isinstance(e['destination'], (ipaddress.IPv4Network, ipaddress.IPv6Network))
            # The gateway might be None if the IPv4 address is 169.254.0.0/16
            assert isinstance(e['gateway'], (ipaddress.IPv4Address, ipaddress.IPv6Address)) or e['gateway'] is None
            assert isinstance(e['dev'], str)
            assert isinstance(e['linkdown'], bool)
        (self.routing_table, self.default_gateway, self.default_dev) = rt
        # Issue 44 is no longer an issue here.
        # Issue 45 negated it.
        # assert self.default_dev != ['dev'], f"default_dev is ['dev'] and that's wrong\n" + str(rt)
        # Issue 45.  Actually, this isn't thorough because there could be more than one default
        # gateway, but it's good enough for now.
        assert isinstance(self.default_gateway[0], (ipaddress.IPv4Address, ipaddress.IPv6Address))
        """
        return

    @property
    def get_default_gateway(self):
        return self.rt[1]

    def get_status(self) -> ErrorLevels:
        return self.layer.get_status()

    def get_routing_table(self, family_ ) -> dict:
        ip_route_list_command = f"ip {self.family_flag} route list"

    # Issue 44 - add a list of default devices in addition to the list of default addresses
    @property
    def parse_ip_route_list_cmd(self) -> Tuple[List[Dict[str, str]], List, List]:
        """
        This method runs the ip route list command and parses the output
        It's here because the output of the ip -4 route list command and the
        ip -6 route list command are very similar
        :return a list of routes.  Each route is a dictionary of the fields of a route
                            in the routing table
        """

        # https://docs.python.org/3/library/subprocess.html
        """
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
        """
        results = Os.run_command(command=[IP_COMMAND, self.family_flag, 'route', 'list'])
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
        # That would be a misconfiguration.  No, it wouldn't.  It might be the case that a second interface was brought
        # up using DHCP.  The dhcpd might tell the interface that it's the default, but the first interface was already
        # the default.  It would be an interesting experiment to down the first interface and see if the system keeps
        # working.
        default_gateway = []
        default_dev = []
        for line in lines:  # lines is the output of the ip route list command
            fields = line.split()
            # Route should become a Route class and not a dict
            route = dict()  # route is a description of a route.  It is keyed by the name of a field in the output
            # of the ip route.  The first field is an address/subnet mask combination, so handle it
            # specially
            if fields[0] == "default":
                assert fields[1] == "via", f"fields[1] should be 'via' but is {fields[1]}.\n" + str(fields)
                if self.family == socket.AF_INET:
                    destination = ipaddress.IPv4Network("0.0.0.0/0")
                else:
                    destination = ipaddress.IPv6Network("::/0")
                # Issue 45
                default_gateway.append(ipaddress.ip_address(fields[2]))
                assert fields[3] == "dev", f"fields[3] should be 'dev' but is {fields[3]}.\n" + str(fields)
                default_dev.append(fields[4])
            # IPv4 loop back address does not have a routing table entry
            else:
                destination = ipaddress.ip_network(fields[0])
            route['destination'] = destination

            # fields[1] is a special case
            if fields[1] == "via":
                assert fields[3] == 'dev', "Parse error in parse_ip_route_list_cmd:" \
                                           f"fields[3] should be 'dev' but is actually {fields[3]}."
                route["gateway"] = ipaddress.ip_address(fields[2])
                route["dev"] = fields[4]
            elif fields[1] == "dev":
                route["gateway"] = None  # Not really a route, but rather a
                # marker to the kernel to tell which device these packets should go to
                route["dev"] = fields[2]
            else:
                raise AssertionError(f"fields[1] can be 'via' or 'dev' but it's actually {fields[1]}")

            # There is actually a redundant assignment of routes['dev'] but it's too complicated to fix now
            route["linkdown"] = False  # Until we see otherwise
            for i in range(3, len(fields) - 1, 2):
                if fields[i] == "linkdown":
                    route["linkdown"] = True
                    # linkdown is a flag, not the title of a field.  No value follows it
                    break
                route[fields[i]] = fields[i + 1]
            route_list.append(route)
        return route_list, default_gateway, default_dev

    # Issue 43 - https://github.com/jeffsilverm/nbmdt/issues/43  Return constants.ErrorLevels, not a tuple
    # Issue 45 - https://github.com/jeffsilverm/nbmdt/issues/45 use the ipaddress type
    def ping(self, address: Union[List, ipaddress.ip_address, str], count: str = "4", min_for_good: int = 8,
             slow_ms: float = 100.0,
             production=False) -> ErrorLevels:
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
        print(sys.stderr, "++++++++ This is all wrong.  Since the ping command wants a string, give it a string +++++")
        if isinstance(address, list):
            address = address[0]
        if isinstance(address, str ):
                """
>>> data = socket.getaddrinfo("f5.com", port=None, family=socket.AF_INET)
>>> data
>>> data[0][4][0]
'107.162.162.40'
>>> data = socket.getaddrinfo("f5.com", port=None, family=socket.AF_INET6)
>>> data[0][4][0]
'2604:e180:1047::ffff:6ba2:b09a'
>>> 
>>> data = socket.getaddrinfo("107.162.162.40", port=None, family=socket.AF_INET6)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/usr/lib/python3.8/socket.py", line 918, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
socket.gaierror: [Errno -9] Address family for hostname not supported
>>> data = socket.getaddrinfo("2604:e180:1047::ffff:6ba2:b09a", port=None, family=socket.AF_INET6)
>>> data[0][4][0]
'2604:e180:1047::ffff:6ba2:b09a'
>>> 
                """
                try:
                    this_address = socket.getaddrinfo(address, port=None, family=self.family)
                    this_address = this_address[0][4][0]
                except ( ValueError, socket.gaierror ) as ve :
                    print(sys.stderr, f"Tried to convert {address} to address using family {self.family} {ve}")
                    raise
        else:
            # This covers the case if address is an instance of IPv6address or IPv4Address
            this_address = address
        # A check that any of the conversion processes above produced an ip_adddress
        assert isinstance(this_address, (ipaddress.IPv6Address, ipaddress.IPv4Address)), \
            "address should be an ipaddress.IPv4Address or an ipaddress.IPv6Address, but it's an" \
            f"{type(this_address)}, {str(this_address)}. "

        # Issue 11 starts here https://github.com/jeffsilverm/nbmdt/issues/11
        # -c is for linux, use -n for windows.
        # https://github.com/jeffsilverm/nbmdt/issues/44
        # This is complicated, and it needs to be complicated for IPv6 becauseadd
        # IPv4 doesn't need to know the interface.
        if self.family == socket.AF_INET6 and this_address not in ipaddress.IPv6Network("2000::/3"):
            # Is this a Globally Unique Address?  It is if the MSB 3 bits are 001.  By convention,
            # if the value of the first 4 bits is 2, then the address is a GUA.
            # If we're here, then this is not a GUA
            # For now, I am going to make the simplifying assumption that if we're *not*
            # pinging a GUA, then we are pinging the link local gateway, which is the in default_gateway
            # attribute, via the device in the default_dev attribute.
            if this_address not in self.dgw:
                self.dump_network_obj()
                raise AssertionError(f"Trying to ping a non-GUA IPv6 address {str(this_address)}"
                f"that is a the default gateway {str(self.dgw)}")
            else:
                # Not sure how to deal with the case where there is more than one default device.
                # I will deal with that when I come to it.
                dev = self.default_dev[0]
                assert isinstance(dev, str)
            args = [PING_COMMAND, self.family_flag, '-c', count, '-I', dev, str(this_address), '-n']
        else:
            args = [PING_COMMAND, self.family_flag, '-c', count, str(this_address), '-n']
        cpi = subprocess.run(args=args,
                             stdin=None,
                             input=None,
                             stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None,
                             check=False, encoding="utf-8", errors=None)
        # return status = 0 if everything is okay
        # return status = 2 if DNS fails to look up the name
        # return status = 1 if the device is not pingable
        # I think this is too draconian
        if cpi.returncode == 2:
            raise utilities.DNSFailure(name=this_address, query_type=('A' if self.family == socket.AF_INET else 'AAAA'))
        elif cpi.returncode != 0 and cpi.returncode != 1:
            cprint(
                f"About to raise a subprocess.CalledProcessError exception. name={this_address} cpi={cpi} returncode is "
                f"{cpi.returncode}",
                'red', file=sys.stderr)
            raise subprocess.CalledProcessError
        elif cpi.returncode == 1 and production:
            raise NotPingable(name=str(this_address))
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
            utilities.report(f"Found default {self.family_str} gateway {self.default_gateway[0]}.",
                             severity=ErrorLevels.NORMAL)
        elif num_def_gateways > 1:
            utilities.report(f"Found multiple default {self.family_str} gateways {str(self.default_gateway)}.",
                             severity=ErrorLevels.OTHER)
        elif num_def_gateways == 0:
            utilities.report(f"Found NO default {self.family_str} gateway", severity=ErrorLevels.DOWN)

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
    for r in ipv4_routing_table.route_list:
        print(r.__str__())
        print(f"Destination network {r['destination']} gateway router {r['gateway']}")
    print(40 * "=")
    for r in ipv6_routing_table.route_list:
        print(r.__str__())
        print(f"Destination network {r['destination']} gateway router {r['gateway']}")
    print(40 * "-")
    inet_dgw: list = ipv4_routing_table.dgw
    print(
        f"The default IPv4 gateway {inet_dgw} is "
        f"{('' if ipv4_routing_table.ping(inet_dgw, production=False) else 'NOT')} pingable")
    for t in ["208.97.189.29", "Commercialventvac.com", "ps558161.dreamhost.com", 'google.com']:
        print(f"{t} is {('' if ipv4_routing_table.ping(t, production=False) else 'NOT')} pingable")
    print(40 * ".")
    inet6_dgw = ipv6_routing_table['default_gateway'][0]
    print(
        f"The default IPv6 gateway {inet6_dgw} is "
        f"{('' if ipv6_routing_table.ping(inet6_dgw, production=False) else 'NOT')} pingable")
    for t in ["2607:f298:5:115f::23:e397", "Commercialventvac.com", "ps558161.dreamhost.com", 'google.com']:
        try:
            print(f"{t} is {('' if ipv6_routing_table.ping(t, production=False) else 'NOT')} pingable")
        except utilities.DNSFailure as u:
            cprint(f"There was a DNS failure exception {str(u)} on {t}.  Continuing")
    print(40 * "-")
