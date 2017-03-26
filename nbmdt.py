#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#



import sys
import subprocess


class Physical_Interface ( object ):
    """This object contains all of the information about a physical interface. """

    def __init__ ( self, name, tx_errors, tx_packets, rx_errors, rx_packets, flags  ) :

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




class Date_Link (object ) :
    """This object contains the the data link parameters, such as the MAC address, Note that an interface can have more
    than one IPv4 or IPv6 address, so there is a one to many relationship between interfaces and """

    def __init__ ( self, name, mac_addresses,  ):

        self.name = name
# Interestingly enough, it is possible to have multiple MAC addresses on a single physical interface.  I didn't know that
# http://serverfault.com/questions/223601/multiple-mac-addresses-on-one-physical-network-interface-linux
        self.mac_address = mac_addresses

class IPv4_address ( object ) :
    """This object has an IPv4 object"""

    def __init__ ( self, name, ipv4_address ) :

        self.name = name
        self.ipv4_address


class IPv6_address ( self, object ) :

    def __init__ ( self, name, ipv6_address ):

        self.name = name
        self.ipv6_address


class IPv4_route ( object ) :

# jeffs@jeffs-laptop:~$ /sbin/route
# Kernel IP routing table
# Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
# 0.0.0.0         192.168.8.1     0.0.0.0         UG    600    0        0 wlp12s0
# 192.168.8.0     0.0.0.0         255.255.255.0   U     600    0        0 wlp12s0
# 192.168.122.0   0.0.0.0         255.255.255.0   U     0      0        0 virbr0

    def __init__ ( self, name, ipv4_destination, ipv4_gateway, ipv4_mask, ipv4_flags, ipv4_metric, ipv4_ref, ipv4_use, \
                   ipv4_interface  ) :

        self.name = name
        self.ipv4_destination = ipv4_destination
        self.ipv4_gateway = ipv4_gateway
        self.ipv4_mask = ipv4_mask
        self.ipv4_flags = ipv4_flags
        self.ipv4_metric = ipv4_metric
        self.ipv4_mask = ipv4_mask
        self.ipv4_ref = ipv4_ref
        self.ip4v_use = ipv4_use
        self.ipv4_interface = ipv4_interface


class IPv6_route (object ):


# Kernel IPv6 routing table
# Destination                    Next Hop                   Flag Met Ref Use If
# 2601:602:9802:93a8::/64        ::                         UAe  256 0     0 eno1
# 2601:602:9802:93a8::/64        ::                         UAe  256 0     0 enp3s0
# fe80::/64                      ::                         U    256 0     0 eno1
# fe80::/64                      ::                         U    256 0     0 enp3s0
# ::/0                           fe80::2e30:33ff:fe55:ca5f  UGDAe 1024 8 15656 eno1
# ::/0                           fe80::2e30:33ff:fe55:ca5f  UGDAe 1024 0     0 enp3s0
# ::/0                           ::                         !n   -1  1 24572 lo
# ::1/128                        ::                         Un   0   9   869 lo
# 2601:602:9802:93a8::/128       ::                         Un   0   1     0 lo
# 2601:602:9802:93a8::/128       ::                         Un   0   1     0 lo
# 2601:602:9802:93a8:210:18ff:fecc:9c77/128 ::                         Un   0   1     0 lo
# 2601:602:9802:93a8:222:4dff:fe7c:4dd9/128 ::                         Un   0   4 80408 lo
# fe80::/128                     ::                         Un   0   1     0 lo
# fe80::/128                     ::                         Un   0   1     0 lo
# fe80::210:18ff:fecc:9c77/128   ::                         Un   0   3     3 lo
# fe80::222:4dff:fe7c:4dd9/128   ::                         Un   0   5  2876 lo
# ff00::/8                       ::                         U    256 8 15855 eno1
# ff00::/8                       ::                         U    256 8 14176 enp3s0
# ::/0                           ::                         !n   -1  1 24572 lo

    def __init__ ( self, name, ipv6_destination, ipv6_next_hop, ipv6_flags, ipv6_metric, ipv6_ref, ipv6_use, \
                   ipv6_interface ):

        self.name = name
        self.ipv6_destination = ipv6_destination
        self.ipv6_next_hop = ipv6_next_hop
        self.ipv6_flags = ipv6_flags
        self.ipv6_metric = ipv6_metric
        self.ipv6_ref = ipv6_ref
        self.ipv6_use = ipv6_use
        self.ipv6_interface = ipv6_interface


    def find_routing_table ( self ):
        """This method returns an IPv6 routing table.  In version 1, this is done by running the route command and
        scrapping the output.  A future version will query the routing table through the /sys pseudo file system"""


        scraped_route_table = subprocess.
# This is the recommend approach for python 3.5 and later  From https://docs.python.org/3/library/subprocess.html
        subprocess.run(["/sbin/route", "-n", "-6"], stdin=None, input=None, stdout=None, stderr=None, shell=False, timeout=None,
                       check=False, encoding=None, errors=None)









class System_Description ( object ):
    """Refer to the OSI stack, for example, at https://en.wikipedia.org/wiki/OSI_model.  Objects of this class describe
     the system, including interfaces, IPv4 and IPv6 addresses, routes, applications.  Each of these objects have a test
     associated with them"""

    def  __init__ ( self, interfaces, ipv4_addresses, ipv6_addresses, ipv4_routes, applications, name  ):

        self.interfaces = interfaces
        self.ipv4_addresses = ipv4_addresses
        self.ipv6_addresses = ipv6_addresses
        self.ipv4_routes = ipv4_routes
        self.ipv6_routes = ipv6_routes
        self.applications = applications
        self.name = name


    def populate_nominal () :
        """This method goes through a system that is nominally configured and operating and records the configuration """

        applications = find_applications()
        ipv4_routes = find_ipv4_routes()
        ipv6_routes = find_ipv6_routes()
        ipv6_addresses = find_ipv6_addresses ()
        ipv4_addresses = find_ipv4_addresses ()
        interfaces = find_interfaces ()




mode = parse_arguments(sys.argv)


nominal = System_description ( )