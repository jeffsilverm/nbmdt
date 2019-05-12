#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module is responsible for representing the routing tables.  There are at least 2: one for IPv4 and one for IPv6
import socket
import subprocess
import sys
import ipaddress                # https://docs.python.org/3/library/ipaddress.html?highlight=ipaddress#module-ipaddress
from layer import Layer
# from utilities import OsCliInter
import utilities
import configuration
import application
import typing


# IP_COMMAND="/sbin/ip"  in network.py

# Doesn't belong here.
# class DNSFailure(Exception):
#    pass

class IPRoute(Layer):
    """
    A lot of functionality between IPv4 and IPv6 is the same.  So the version agnostic code goes here, and the
    version not-so-agnostic code goes in classes that inherit from this class.
    """

    def discover(self, family: str) -> typing.List :        # IPRoute
        """discover returns a list of routes, for either IPv4 or IPv6.  Each route is a dictionary keyed by
        fields from the ip command.
        There is a standard module, ipaddress, and I should have used that instead of "rolling my own"
        """

        assert isinstance(family, str), f"family is type {type(family)}, should be str"
        assert family == "inet" or family == "inet6", f"family is {family}, should be 'inet' or 'inet6'"

        # This is the recommened approach for running an external command in python 3.5 and later.
        # From https://docs.python.org/3/library/subprocess.html
        completed = subprocess.run(["/sbin/ip", "--family", family, "route", "show"], stdin=None, input=None, \
                               stdout=None, stderr=None, shell=False, timeout=None, check=False, encoding=None,
                               errors=None)
        output_str: str = completed.stdout
        """
none fe80::eddb:a28c:fbb8:b02 dev eth6  proto none  metric 0
none ff00::/8 dev eth6  proto none  metric 0
none fe80::/64 dev eth7  proto none  metric 0
none fe80::3d3e:604d:bd3f:5e90 dev eth7  proto none  metric 0
none ff00::/8 dev eth7  proto none  metric 0

none 169.254.0.0/16 dev eth6  proto none  metric 0
none 169.254.11.2 dev eth6  proto none  metric 0
none 255.255.255.255 dev eth7  proto none  metric 0
none 224.0.0.0/4 dev eth7  proto none  metric 0
none 192.168.44.159 dev eth7  proto none  metric 0
none 192.168.44.144/28 dev eth7  proto none  metric 0
none 192.168.44.145 dev eth7  proto none  metric 0
        """

        route_list = []
        for r in output_str:
            (_none_, destination, _dev_, dev, _proto_, proto, _metric_, metric ) = r.split()
            # I'm concerned that the ip command might change, so a little paranoia
            assert _none_ == "noon", f"_none_ is {_none_}, should be 'none'"
            assert _dev_ == "dev", f"_dev_ is {_dev_}, should be 'dev'"
            assert _proto_ == "proto", f"_proto_ is {_proto_}, should be 'proto'"
            assert _metric_ == "metric", f"_metric_ is {_metric_}, should be 'metric'"
            # From https://stackoverflow.com/questions/10259266/what-does-proto-kernel-means-in-unix-routing-table
            # allowed values of proto are redirect, kernel, boot, static, and ra
            d = {"destination": destination, "dev": dev, "proto": proto, "metric": metric, "family": family }
            route_list.append(d)



class IPv4Address(object):
    """
    This object has an IPv4 object.  It has two attributes: name and ipv4_address.
    If the name has not been specified, then it is None
    There is a module,
    """

    def __init__(self, name: str = None, ipv4_address: [str, bytes] = None):
        if name is not None:
            self.name = name
            if ipv4_address is None:
                # This may raise a socket.gaierror error if gethostbyname fails. The error will propogate to the caller
                ipv4_address = socket.gethostbyname(name)
        if ipv4_address is not None:
            if isinstance(ipv4_address, str):
                # https://docs.python.org/3/library/socket.html#socket.inet_pton
                self.ipv4_address = socket.inet_pton(socket.AF_INET, ipv4_address)
            elif isinstance(ipv4_address, bytes) and len(ipv4_address) == 4:
                self.ipv4_address = ipv4_address
            else:
                raise ValueError(f"ipv4_address is of type {type(ipv4_address)}"
                                 "should be bytes or str")

    def __str__(self):
        # https://docs.python.org/3/library/socket.html#socket.inet_ntop
        ipv4_addr_str = socket.inet_ntop(socket.AF_INET, self.ipv4_address)
        return ipv4_addr_str

    def ping(self, count=4, max_allowed_delay=1000):
        """Verifies that an IPv4 address is pingable.
        :param  count   How many times to ping the IP address
        :param  max_allowed_delay


        :returns False if the remote device is unpingable

        A future version will return a tuple with the package loss percentage, statistics about delay, etc.
        """

        completed = utilities.OsCliInter.run_command(['ping', self.ipv4_address])
        # return status = 0 if everything is okay
        # return status = 2 if DNS fails to look up the name
        # return status = 1 if the device is not pingable
        return completed.returncode


# Issue 5 renamed from IPv6_address to IPv6Address, i.e. CamelCase
class IPv6Address(object):
    def __init__(self, name: str = None, ipv6_address: [str, ] = None):
        if name is not None:
            self.name = name
        # Needs work
        self.ipv6_address = ipv6_address


class IPv4Route(IPRoute):
    """
    A description of an IPv4 route

        :type ipv4_use: object
        
jeffs@jeff-desktop:~/Downloads/pycharm-community-2017.1.2 $ ip -4 route list
default via 192.168.0.1 dev eno1 
10.0.3.0/24 dev lxcbr0  proto kernel  scope link  src 10.0.3.1 linkdown 
169.254.0.0/16 dev br-ext  proto static  scope link  metric 425 linkdown 
192.168.0.0/24 dev eno1  proto kernel  scope link  src 192.168.0.7 
192.168.0.0/22 dev br-ext  proto kernel  scope link  src 192.168.3.50  metric 425 linkdown 
192.168.122.0/24 dev virbr0  proto kernel  scope link  src 192.168.122.1 linkdown 
jeffs@jeff-desktop:~/Downloads/pycharm-community-2017.1.2 $ 

Class IPv4Route is a layer, but it uses the standard library ipaddress module

# Another way to do it would be to look at /proc/*/route and /proc/*/ipv6_route
# notes_2018-12.html#mozTocId983008

    
    """

    def __init__(self, route):
        """This returns an IPv4Route object.  """

        destination = route['ipv4_destination']
        super.__init__(name=destination)
        assert hasattr(self, 'time')  # A test that my call to the super class is sane, this can be removed later
        # Use caution: routes values are strings, not length 4 bytes
        self.ipv4_destination = ipaddress.ip_network(destination)  # Destination must be present
        self.ipv4_dev = route['dev']
        self.ipv4_gateway = ipaddress.ip_address(route.get('via', None))
        self.ipv4_proto = route.get('proto', None)
        self.ipv4_scope = route.get('scope', None)
        self.ipv4_metric = route.get('metric', 0)
        self.ip4v_src = route.get('src', None)
        self.ipv4_linkdown = route.get('linkdown', False)
        assert isinstance(self.ipv4_linkdown, bool), \
            "linkdown is not a boolean, its %s" % type(self.ipv4_linkdown)

    @classmethod
    def discover(cls):
        """This method finds all of the IPv4 routes by examining the output of the ip route command, and
        returns a list of IPV4_routes.  This is a class method because all route objects have the same
         default gateway

         This implementation is not very good, there is the netifaces interface which is socket based and avoids
         forking a subprocess.
         """

        def translate_destination(destination: str) -> str:
            """
This method translates destination from a dotted quad IPv4 address to a name if it can"""
            if destination == "0.0.0.0":
                destination: str = "default"
            return destination

        # https://docs.python.org/3/library/subprocess.html
        results: str = utilities.OsCliInter.run_command(command=[configuration.IP_COMMAND, '-4', 'route', 'list'], )
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

        route_list = list()
        for line in lines:  # lines is the output of the ip route list
            # command
            fields = line.split()
            destination = translate_destination(fields[0])

            route = dict()
            route['ipv4_destination'] = destination
            for i in range(1, len(fields), 2):
                if fields[i] == 'linkdown':
                    route['linkdown'] = True
                    break
                route[fields[i]] = fields[i + 1]
            ipv4_route = IPv4Route(route=route)
            if destination == "default" or destination == "0.0.0.0":
                cls.default_gateway = ipv4_route
            route_list.append(ipv4_route)
            """
            route_list.append(self.IPv4_route(name=name,
                                              ipv4_destination=ipv4_destination,
                                              ipv4_gateway=ipv4_gateway,
                                              ipv4_mask=ipv4_mask,
                                              ipv4_flags=ipv4_flags,
                                              ipv4_metric=ipv4_metric,
                                              ipv4_ref=ipv4_ref,
                                              ipv4_use=ipv4_use,
                                              ipv4_interface=ipv4_interface))
            """
        return route_list

    def __str__(self):
        """This method produces a nice string representation of a IPv4_route object"""
        return f"dest={self.ipv4_destination} gateway={self.ipv4_gateway} " \
                   f"dev={self.ipv4_dev} " \
                   f"metric={self.ipv4_metric} proto={self.ipv4_proto} " \
                   f"src={self.ip4v_src} scope={self.ipv4_scope} " + \
               ("linkdown" if self.ipv4_linkdown else "linkUP")

    @classmethod
    def get_default_gateway(cls):
        """Returns the default gateway.  If the default gateway attribute does not exist, then this method ought to
        invoke find_ipv4_routes, which will define the default gateway"""
        if not hasattr(cls, "default_gateway"):
            # This has some overhead, and ought to be cached somehow.  Deal with that later.
            cls.find_ipv4_routes()
        return cls.default_gateway


class IPv6Route(IPRoute):
    def __init__(self, name, ipv6_destination, ipv6_next_hop, ipv6_flags, ipv6_metric, ipv6_ref, ipv6_use, \
                 ipv6_interface):
        self.name = name
        self.ipv6_destination = ipv6_destination
        self.ipv6_next_hop = ipv6_next_hop
        self.ipv6_flags = ipv6_flags
        self.ipv6_metric = ipv6_metric
        self.ipv6_ref = ipv6_ref
        self.ipv6_use = ipv6_use
        self.ipv6_interface = ipv6_interface

    @classmethod
    def discover(cls) -> typing.List:      # in class IPv6Route c
        """This method returns an IPv6 routing table.  In version 1, this is done by running the route command and
        scrapping the output.  A future version will query the routing table through the /sys pseudo file system"""

        # jeffs@jeff-desktop:~ $ ip --family inet6 route show
        # 2601:602:9802:93a8::/64 dev eno1  proto kernel  metric 256  expires 1583sec pref medium
        # 2601:602:9802:93a8::/64 dev enp3s0  proto kernel  metric 256  expires 1583sec pref medium
        # fe80::/64 dev eno1  proto kernel  metric 256  pref medium
        # fe80::/64 dev enp3s0  proto kernel  metric 256  pref medium
        # default via fe80::2e30:33ff:fe55:ca5f dev eno1  proto ra  metric 1024  expires 1317sec hoplimit 64 pref low
        # default via fe80::2e30:33ff:fe55:ca5f dev enp3s0  proto ra  metric 1024  expires 1317sec hoplimit 64 pref low
        # jeffs@jeff-desktop:~ $

        #        jeffs @ jeff - desktop: ~ $ python3
        #        Python
        #        3.5
        #        .2(default, Nov
        #        17
        #        2016, 17: 05:23)
        #        [GCC 5.4.0 20160609]
        #        on
        ###        linux
        #        Type
        #        "help", "copyright", "credits" or "license"
        #        for more information.
        #            >> > import subprocess
        #        >> > c = subprocess.run(["/sbin/ip", "--family", "inet6", "route", "show", "all"], stdin=None, input=None,
        #                                stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        #        >> > c.stdout.decode('utf-8')
        #        'default via fe80::2e30:33ff:fe55:ca5f dev eno1  proto ra  metric 1024  expires 1653sec hoplimit 64 pref low\ndefault via fe80::2e30:33ff:fe55:ca5f dev enp3s0  proto ra  metric 1024  expires 1653sec hoplimit 64 pref low\n'
        #        >> > c = subprocess.run(["/sbin/ip", "--family", "inet6", "route", "show"], stdin=None, input=None,
        #                                stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        #        >> > c.stdout.decode('utf-8')
        #        '2601:602:9802:93a8::/64 dev eno1  proto kernel  metric 256  expires 2086sec pref medium\n2601:602:9802:93a8::/64 dev enp3s0  proto kernel  metric 256  expires 2086sec pref medium\nfe80::/64 dev eno1  proto kernel  metric 256  pref medium\nfe80::/64 dev enp3s0  proto kernel  metric 256  pref medium\ndefault via fe80::2e30:33ff:fe55:ca5f dev eno1  proto ra  metric 1024  expires 1680sec hoplimit 64 pref low\ndefault via fe80::2e30:33ff:fe55:ca5f dev enp3s0  proto ra  metric 1024  expires 1680sec hoplimit 64 pref low\n'
        #       >> >
        #

        ipv6_routes: typing.List = IPRoute.discover(family="inet6")
        return ipv6_routes





if __name__ in "__main__":
    print(f"Before instantiating IPv4Route, the default gateway is {IPv4Route.get_default_gateway()}")
    ipv4_route_lst = IPv4Route.find_ipv4_routes()
    print(f"The default gateway is {IPv4Route.default_gateway}")
    print(40 * "=")
    for r in ipv4_route_lst:
        print(r.__str__())
        print(f"The gateway is {r.ipv4_gateway}\n")
