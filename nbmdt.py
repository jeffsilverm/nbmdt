#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#




import subprocess
import socket
import re






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


class Interface(object):
    """Objects of this class edscribe an interface or a link"""
    def __init__(self, interface ):
        self._interface_comp_pat = "^.*"
        self.interface_name = interface
        self.ipv4_addresses = self.find_ipv4_addresses(interface)
        self.ipv6_addresses = self.find_ipv6_addresses(interface)




    class PhysicalInterface ( object ):


        def __init__  ( self, link_name, link_flags, link_mtu, link_qdisc, link_state, link_mode,
                        link_group, link_qlen, link_link, link_mac, link_brd_mac, link_promiscuity, link_remainder):
            self.link_name = link_name
            self.link_flags =link_flags
            self.link_mtu = link_mtu
            self.link_qdisc = link_qdisc
            self.link_state = link_state
            self.link_mode = link_mode
            self.link_group = link_group
            self.link_qlen = link_qlen
            self.link_link = link_link
            self.link_mac = link_mac
            self.link_brd_mac = link_brd_mac
            self.link_promiscuity = link_promiscuity
            self.link_remainder = link_remainder

        def __str__(self):
            s = "name: " + self.link_name
            s += " flags: " + self.link_flags
            s += " mtu: " + self.link_mtu
            s += " qdisc: " + self.link_qdisc
            s += " state: " + self.link_state
            s += " mode: " + self.link_mode
            s += " group:" + self.link_group
            s += " qlen: " + self.link_qlen
            s += " link: " + self.link_link
            s += " MAC: " + self.link_mac
            s += " BRD_MAC: " + self.link_brd_mac
            s += " promiscuity: " + self.link_promiscuity
            s += " remainder: " + self.link_remainder

            return s



        @classmethod
        def get_all_physical_interfaces(self):
            """This method returns a dictionary of interfaces as known by the ip link list command
            """

            completed = subprocess.run(["/bin/ip", "--details", "--oneline", "link", "list"], stdin=None, input=None,
                                       stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
            completed_str = completed.stdout.decode('ascii')
            links_list = completed_str.split('\n')
            link_db = dict()
            for link in links_list:
                fields = link.split()
                link_name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
                link_flags = fields[2]
                assert "mtu" == fields[3]  # Doesn't really do anything
                link_mtu = fields[4]
                assert "qdisc" == fields[5]  # I don't know what qdisc is
                link_qdisc = fields[6]  # So far, I have seen values noop, pfifo_fast, noqueue, mq
                assert "state" == fields[7]
                link_state = fields[8]
                assert "mode" == fields[9]
                link_mode = fields[10]
                assert "group" == fields[11]
                link_group = fields[12]
                assert "qlen" == fields[13]
                link_qlen = fields[14]
                link_link = fields[15]
                link_mac = fields[16]
                assert "brd" == fields[17]
                link_brd_mac = fields[18]
                assert "promiscuity" == fields[19]
                link_promiscuity = fields[20]
                link_remainder = fields[21:]  # I don't what these do, either.
                link_db[link_name] = self.PhysicalInterface(link_name, link_flags, link_mtu, link_qdisc, link_state,
                                                       link_mode,
                                                       link_group, link_qlen, link_link, link_mac, link_brd_mac,
                                                       link_promiscuity, link_remainder)

            return link_db

    # There should be a class method here that contains a dictionary of all of the PhysicalInterfaces


    class LogicalInterface ( object ) :

        def __init__(self, addr_name, addr_family, addr_addr, addr_brd, addr_scope,
                                                    addr_remainder ):
            """This creates a logical interface object."""
            if addr_family != "inet" and addr_family != "inet6" :
                raise ValueError ("misunderstood value of addr_family: {}".format( addr_family ))
            self.addr_name=addr_name
            self.addr_family=addr_family
            self.addr_addr=addr_addr
            self.addr_brd=addr_brd
            self.addr_scope=addr_scope
            self.addr_remainder=addr_remainder

        def __str__(self):
            s = " name: " + self.addr_name
            s += " family:" + self.addr_family
            s += " address: " + self.addr_addr
            if self.addr_family == "inet" :
                s += " Broadcast: " + self.addr_brd
            s += " scope: " + self.addr_scope
            s += " remaining: " + self.addr_remainder
            return s




    # There should be a class method here that contains a dictionary of all of the LogicalInterfaces




    @classmethod
    def get_all_logical_interfaces(self):
        """This method returns a dictionary of logical interfaces as known by the ip address list command"""

        completed = subprocess.run(["/bin/ip", "--oneline", "address", "list"], stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        addrs_list = completed_str.split('\n')
        addr_db=dict()
        for addr in addrs_list :
            fields = addr.split()
            addr_name = fields[1]
            addr_family = fields[2]
            addr_addr = fields[3]
            if addr_family == "inet" :
                assert "brd" == fields[4]
                addr_brd = fields[5]
                assert "scope" == fields[6]
                addr_scope = fields[7]
                addr_remainder = fields[8:]
            elif addr_family == "inet6" :
                addr_brd = None                 # for IPv6
                assert "scope" == fields[4]
                addr_scope == fields[5]
                addr_remainder = fields[6]
            else :
                raise ValueError ("misunderstood value of addr_family: {}".format( addr_family ))
            addr_db[addr_name] = self.LogicalInterface ( addr_name, addr_family, addr_addr, addr_brd, addr_scope,
                                                    addr_remainder )






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
        # To find all IPv4 machines on an ethernet, use arp -a     See ipv4_neighbors.txt

        # To find all IPv6 machines on an ethernet, use ip -6 neigh show



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
    # nominal = SystemDescription.describe_current_state()
    link_db = PhysicalInterface.get_all_physical_interfaces()

