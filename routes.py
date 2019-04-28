#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module is responsible for representing the routing tables.  There are at least 2: one for IPv4 and one for IPv6


class IPv4_address(object):
    """This object has an IPv4 object"""

    def __init__(self, name, ipv4_address):
        self.name = name
        self.ipv4_address = ipv4_address


class IPv6_address(object):
    def __init__(self, name, ipv6_address):
        self.name = name
        self.ipv6_address = ipv6_address


class IPv4Route(object):
    """
    A description of an IPv4 route

        :type ipv4_use: object
        


    
    """

    def __init__(self, destination, route_dict: dict ) -> None:
        """This returns an IPv4Route object.  The object can come from one of two sources: this constructor can
        query the system using the ip command or it can go to the configuration file"""

        assert isinstance(destination, ipaddress.IPv4Address), \
            "destination should be an instance of IPv4Address, but is actually {type(destination)}"
        self.ipv4_destination = destination
        for key in route_dict.keys():
            assert key in ["dev", "via", "proto", "scope", "src", "metric", "linkdown"], \
            setatttr(self, key, route_dict[key])


    @staticmethod
    def find_ipv4_routes(self):
        """This method finds all of the IPv4 routes by examining the output of the ip route command, and
        returns a list of IPV4_routes """
        # https://docs.python.org/3/library/subprocess.html
        # Issue 39 
        cpi = subprocess.run(['ip', '-4', 'route', 'list'], stdin=None, input=None, stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None,
                             check=False, encoding="utf-8", errors=None)
        if cpi.returncode != 0:
            raise subprocess.CalledProcessError
        """
jeffs@jeff-desktop:~/Downloads/pycharm-community-2017.1.2 $ ip -4 route list
default via 192.168.0.1 dev eno1 
10.0.3.0/24 dev lxcbr0  proto kernel  scope link  src 10.0.3.1 linkdown 
169.254.0.0/16 dev br-ext  proto static  scope link  metric 425 linkdown 
192.168.0.0/24 dev eno1  proto kernel  scope link  src 192.168.0.7 
192.168.0.0/22 dev br-ext  proto kernel  scope link  src 192.168.3.50  metric 425 linkdown 
192.168.122.0/24 dev virbr0  proto kernel  scope link  src 192.168.122.1 linkdown 
jeffs@jeff-desktop:~/Downloads/pycharm-community-2017.1.2 $ 
        """
        # Because subprocess.run was called with encoding=utf-8, output will be a string
        routes = cpi.stdout.decode('utf-8')
        route_records = routes.split('\n')
        route_list = list()
        for r_rec in route_records:
            route_dict = Dict()
            words = r_rec.split()
            if "default" == word[0] :
                word[0] == "0.0.0.0/32"
            ipv4_destination = ipaddress.IPv4Network(word[0])
            for i in range(1, len(words), 2):
                word = words[i]
                if "linkdown" == word:
                    route_dict[word] = True
                else:
                    route_dict[word]=words[i+1]
            if "linkdown" not in words:
                route_dict["linkdown"] = False
            route_list.append(IPv4_route(name, ipv4_destination, route_dict))
                                         
        return route_list

    def __str__(self):
        """This method produces a nice string representation of a IPv4_route object"""
        return "name={} dest={} gateway={} mask={} flags={} metric={} ref={} use={} I/F={}".format( \
            self.name, self.ipv4_destination, self.ipv4_gateway, self.ipv4_mask, self.ipv4_flags, \
            self.ipv4_metric, self.ipv4_ref, self.ip4v_use, self.ipv4_interface)


class IPv6Route(object):
    def __init__(self, name, ipv6_destination, ipv6_next_hop, ipv6_flags, ipv6_metric, ipv6_ref, ipv6_use, \
                 ipv6_interface):
        raise AssertionError("Needs to be rewritten as IPv4Route is written")
        self.name = name
        self.ipv6_destination = ipv6_destination
        self.ipv6_next_hop = ipv6_next_hop
        self.ipv6_flags = ipv6_flags
        self.ipv6_metric = ipv6_metric
        self.ipv6_ref = ipv6_ref
        self.ipv6_use = ipv6_use
        self.ipv6_interface = ipv6_interface

    def find_ipv6_routes(self):
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

        # This is the recommend approach for python 3.5 and later  From https://docs.python.org/3/library/subprocess.html
        completed = subprocess.run(["/sbin/ip", "--family", "inet6", "route", "show"], stdin=None, input=None, \
                                   stdout=None, stderr=None, shell=False, timeout=None, check=False, encoding=None,
                                   errors=None)
        route_list = []
        for r in completed:
            (ipv6_desstination, _dev_, ipv6_interface,) = r.split()


