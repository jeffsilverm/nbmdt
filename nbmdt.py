#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#




import subprocess
import socket
import re


class Physical_Interface(object):
    """This object contains all of the information about a physical interface. """

    def __init__(self, name, tx_errors, tx_packets, rx_errors, rx_packets, flags):
        self.name = name
        self.tx_errors = tx_errors
        self.rx_errors = rx_errors
        self.tx_packets = tx_packets
        self.rx_packets = rx_packets
        self.flags = flags


# wlp12s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500   <=== name, Physical
#        inet 192.168.8.47  netmask 255.255.255.0  broadcast 192.168.8.255 < === Network layer
#        inet6 fe80::ff55:4405:3d95:aa34  prefixlen 64  scopeid 0x20<link> <== Network layer
#        ether 00:21:6a:53:14:10  txqueuelen 1000  (Ethernet)         <=== data link layer
#        RX packets 98009  bytes 69438196 (66.2 MiB)     <=== name, Physical
#        RX errors 0  dropped 0  overruns 0  frame 0     <=== name, Physical
#        TX packets 67467  bytes 16935624 (16.1 MiB)     <=== name, Physical
#        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0     <=== name, Physical




class Date_Link(object):
    """This object contains the the data link parameters, such as the MAC address, Note that an interface can have more
    than one IPv4 or IPv6 address, so there is a one to many relationship between interfaces and """

    def __init__(self, name, mac_addresses, ):
        self.name = name
        # Interestingly enough, it is possible to have multiple MAC addresses on a single physical interface.  I didn't know that
        # http://serverfault.com/questions/223601/multiple-mac-addresses-on-one-physical-network-interface-linux
        self.mac_address = mac_addresses


class IPv4_address(object):
    """This object has an IPv4 object"""

    def __init__(self, name, ipv4_address):
        self.name = name
        self.ipv4_address = ipv4_address


class IPv6_address(object):
    def __init__(self, name, ipv6_address):
        self.name = name
        self.ipv6_address = ipv6_address


class IPv4_route(object):
    """
    A description of an IPv4 route

        :type ipv4_use: object
    """

    def __init__(self, name, ipv4_destination, ipv4_gateway, ipv4_mask, ipv4_flags, ipv4_metric, ipv4_ref,
                 ipv4_interface, ipv4_use):


        self.name = name
        self.ipv4_destination = ipv4_destination
        self.ipv4_gateway = ipv4_gateway
        self.ipv4_mask = ipv4_mask
        self.ipv4_flags = ipv4_flags
        self.ipv4_metric = ipv4_metric
        self.ipv4_ref = ipv4_ref
        self.ip4v_use = ipv4_use
        self.ipv4_interface = ipv4_interface

    # jeffs@jeffs-laptop:~$ /sbin/route
    # Kernel IP routing table
    # Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
    # 0.0.0.0         192.168.8.1     0.0.0.0         UG    600    0        0 wlp12s0
    # 192.168.8.0     0.0.0.0         255.255.255.0   U     600    0        0 wlp12s0
    # 192.168.122.0   0.0.0.0         255.255.255.0   U     0      0        0 virbr0

    @staticmethod
    def find_ipv4_routes(self):
        """This method finds all of the IPv4 routes by examining the output of the ip route command, and
        returns a list of IPV4_routes """
        # https://docs.python.org/3/library/subprocess.html
        cpi = subprocess.run(['route', '-4', '-n'], stdin=None, input=None, stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None,
                             check=False, encoding="utf-8", errors=None)
        if cpi.returncode != 0:
            raise subprocess.CalledProcessError
        # Because subprocess.run was called with encoding=utf-8, output will be a string
        routes = cpi.stdout.decode('utf-8')
        route_records = routes.split('\n')
        route_list = list()
        for r_rec in route_records[2:]:
            (ipv4_destination, ipv4_gateway, ipv4_mask, ipv4_flags, ipv4_metric, ipv4_ref, ipv4_use, \
             ipv4_interface) = r_rec.split()
            if ipv4_destination == "0.0.0.0":
                name = "default"
            else:
                try:
                    name = socket.gethostbyaddr(ipv4_destination)
                except socket.herror as h:
                    # This shouldn't happen, but the documentation says that it can so I have to handle it
                    print("socket.gethostbyaddr")
                    name = ipv4_destination
            route_list.append(IPv4_route(name, ipv4_destination, ipv4_gateway, ipv4_mask, ipv4_flags, ipv4_metric, \
                                         ipv4_ref, ipv4_use, ipv4_interface))
        return route_list

    def __str__(self):
        """This method produces a nice string representation of a IPv4_route object"""
        return "name={} dest={} gateway={} mask={} flags={} metric={} ref={} use={} I/F={}".format( \
            self.name, self.ipv4_destination, self.ipv4_gateway, self.ipv4_mask, self.ipv4_flags, \
            self.ipv4_metric, self.ipv4_ref, self.ip4v_use, self.ipv4_interface)


class IPv6_route(object):
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


class Interfaces(object):
    def __init__(self, interface ):
        self._interface_comp_pat = "^.*"
        self.interface_name = interface
        self.ipv4_addresses = self.find_ipv4_addresses(interface)
        self.ipv6_addresses = self.find_ipv6_addresses(interface)


    @staticmethod
    def find_interfaces(self):
        """This returns a list of all the interfaces using the ifconfig -a command.  cpi is a completed process
        instance"""

        interface_cp = r"^(.*)\s(.*)$"

        cpi = subprocess.run(['/sbin/ifconfig', '-a'], stdin=None, input=None, stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None, check=False, encoding="utf-8", errors=None)
        if cpi.returncode != 0:
            raise subprocess.CalledProcessError
        # Because subprocess.run was called with encoding=utf-8, output will be a string
        ifconfig_out = cpi.stdout.decode('utf-8')
        ifconfig_lines = ifconfig_out.split('\n')
        interface_list = list()
        for line in ifconfig_lines:
            m = re.search(interface_cp, line)
            interface = m.group(1)
            if interface is not None:
                interface_list.append( Interfaces(interface) )
        return interface_list

    # Not a static method because it needs the ifconfig_lines to get the IPv6 addresses
    def find_ipv6_addresses(self, interface):
        raise NotImplementedError

    def find_ipv4_addresses(self, interface):
        raise NotImplementedError


class Networks(object):
    def __init__(self):
        self.remote_hosts = []

    @staticmethod
    def find_networks():
        pass


class Applications(object):
    def __init__(self):
        self.applications = []

    @staticmethod
    def find_applications():
        pass


class SystemDescription(object):
    """Refer to the OSI stack, for example, at https://en.wikipedia.org/wiki/OSI_model.  Objects of this class describe
     the system, including interfaces, IPv4 and IPv6 addresses, routes, applications.  Each of these objects have a test
     associated with them"""

    def __init__(self, interfaces, ipv4_addresses, ipv6_addresses, ipv4_routes, ipv6_routes, applications, name, \
                 networks):

        self.interfaces = interfaces
        self.ipv4_addresses = ipv4_addresses
        self.ipv6_addresses = ipv6_addresses
        self.ipv4_routes = ipv4_routes
        self.ipv6_routes = ipv6_routes
        self.applications = applications
        self.networks = networks
        self.name = name

    @staticmethod
    def describe_current_state():
        """This method goes through a system that is nominally configured and operating and records the configuration """

        applications = Applications.find_applications()
        ipv4_routes = IPv4_route.find_ipv4_routes()
        ipv6_routes = IPv6_route.find_ipv6_routes()
        ipv6_addresses = Interfaces.find_ipv6_addresses()
        ipv4_addresses = Interfaces.find_ipv4_addresses()
        interfaces = Interfaces.find_interfaces()
        networks = Networks.find_networks()

        return (applications, ipv4_routes, ipv6_routes, ipv4_addresses, ipv6_addresses, interfaces, networks)

    def __str__(self):
        """This generates a nicely formatted report of the state of this system"""
        result = "Applications:\n" + "*" * 80
        for app in self.applications:
            result += str(app) + "\n"
        result = result + "\nIPv4 routes\n" + "*" * 80
        for r4 in self.ipv4_routes:
            result += str(r4) + "\n"
        result = result + "\nIPv6 routes\n" + "*" * 80
        for r6 in self.ipv6_routes:
            result += str(r6) + "\n"
        result = result + "\ninterfaces\n" + "*" * 80
        for iface in self.interfaces:
            result += str(iface) + "\n"
        result = result + "\nNetworks:\n" + "*" * 80
        for network in self.networks:
            result += str(network) + "\n"
        return result


if __name__ == "__main__":
    nominal = SystemDescription.describe_current_state()
