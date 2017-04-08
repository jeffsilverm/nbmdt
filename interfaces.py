#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import datetime

class Interfaces(object):

    def __init__ (self ):
        """When you instantiate an Interfaces objects, the class gets a list of all of the characterists of all of the
        network interfaces that ifconfig knows about"""

        # These regexes are relatively low quality.  My assumption is that the socket.gethostbyname and
        # socket.getaddrinfo will raise an exception if the address is ill-formed
        # In the output of the ifconfig command, an interface name begins at the start of a line and ends at the first :

        self.interface_name_cp = re.compile( """"^(.*)\sflags=(.*) mtu \d+$""" )       # Used to extract the interface name
        # From https://www.safaribooksonline.com/library/view/regular-expressions-cookbook/9781449327453/ch08s16.html
        self.inet4_cp = re.compile( """inet (.*?)  netmask (.*?) boadcast (.*?)$""")
        self.inet6_cp = re.compile( """inet6\s(.*?)\sprefixlen \d{1:3}\s\sscopeid\s(0[xX][0-9a-fA-F]+)""")
        self.ethernet_cp = """\s([0-9a-fA-f]{0:4}:+)\s\sprefixlen\s(\d+)\sscopeid\s0x([o-9a-fA-F])<.*>$"""
        self.packets_cp = """RX packets (\d+)"""


        self.ifconfig_lines = self.read_ifconfig(  None )
        self.interface_list = self.create_interface_list()
        self.last_modified_time = datetime.datetime.now()

    # wlp12s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500   <=== name, Physical
    #        inet 192.168.8.47  netmask 255.255.255.0  broadcast 192.168.8.255 < === Network layer
    #        inet6 fe80::ff55:4405:3d95:aa34  prefixlen 64  scopeid 0x20<link> <== Network layer
    #        ether 00:21:6a:53:14:10  txqueuelen 1000  (Ethernet)         <=== data link layer
    #        RX packets 98009  bytes 69438196 (66.2 MiB)     <=== name, Physical
    #        RX errors 0  dropped 0  overruns 0  frame 0     <=== name, Physical
    #        TX packets 67467  bytes 16935624 (16.1 MiB)     <=== name, Physical
    #        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0     <=== name, Physical




    def read_ifconfig (self, interface=None ):
        """Returns the output of the ifconfig as a list of strings.  If interfaces is None, then it uses the -a to get
        all of the interfaces, otherwise it returns just the interface asked for"""

        switch = "-a" if interface==None else interface

        cpi = subprocess.run(['/sbin/ifconfig', switch ], stdin=None, input=None, stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None, check=False, encoding="utf-8", errors=None)
        if cpi.returncode != 0:
            raise subprocess.CalledProcessError
        # Because subprocess.run was called with encoding=utf-8, output will be a string
        ifconfig_out = cpi.stdout.decode('utf-8')
        ifconfig_lines = ifconfig_out.split('\n')
        return ifconfig_lines


    def parse_if_config ( self, ifconfig_lines=None ):
        """accepts the list of lines returned by read_ifconfig or other source and returns two objects in a tuple.  The
        first object is the physical interface and the second object is the logical interface"""
        if ifconfig_lines == None :
            ifconfig_lines = self.ifconfig_lines
        for line in ifconfig_lines :
            line_1_grps = re.search(self.interface_cp, self.ifconfig_lines[0])    # iterface_cp is the compiled pattern
            name = line_1_grps.group(0)
            rest_of_line = line_1_grps.group(1)





    def create_interface_list ( self ):
        interface_list = list()
        for line in self.ifconfig_lines:
            m = re.search(self.interface_cp, line)
            interface_name = m.group(1)
            if interface is not None:
                # Create a named tuple with the name, a logical interface object, a physical interface object.
                interface_list.append( interface_name )
        return interface_list


    class PhysicalInterface(object):
         """This object contains all of the information about a physical interface. """

        def __init__(self, name, tx_errors, tx_packets, rx_errors, rx_packets, flags):
            """This returns an object with the parameterss associated with the physical interface: packert counters,
            the MAC address, """
            self.name = name
            self.tx_errors = tx_errors
            self.rx_errors = rx_errors
            self.tx_packets = tx_packets
            self.rx_packets = rx_packets
            self.flags = flags




	class LogicalInterface( objct ):

        def __init__(self, name, flags, mtu, inet4_address, inet6_addresses, prefixlen, scopeid,):
            """Thia creates a logical interface object"""


