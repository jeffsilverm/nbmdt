#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import datetime
import collections

class Interfaces(object):

    def __init__ (self ):
        """When you instantiate an Interfaces objects, the class gets a list of all of the characterists of all of the
        network interfaces that ifconfig knows about"""

        # These regexes are relatively low quality.  My assumption is that the socket.gethostbyname and
        # socket.getaddrinfo will raise an exception if the address is ill-formed
        # In the output of the ifconfig command, an interface name begins at the start of a line and ends at the first :


        self.ifconfig_lines = self.read_ifconfig(  None )
        self.interface_list = self.create_interface_list()
        self.last_modified_time = datetime.datetime.now()

    # On my laptop running
    # wlp12s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500   <=== name, Physical
    #        inet 192.168.8.47  netmask 255.255.255.0  broadcast 192.168.8.255 < === Network layer
    #        inet6 fe80::ff55:4405:3d95:aa34  prefixlen 64  scopeid 0x20<link> <== Network layer
    #        ether 00:21:6a:53:14:10  txqueuelen 1000  (Ethernet)         <=== data link layer
    #        RX packets 98009  bytes 69438196 (66.2 MiB)     <=== name, Physical
    #        RX errors 0  dropped 0  overruns 0  frame 0     <=== name, Physical
    #        TX packets 67467  bytes 16935624 (16.1 MiB)     <=== name, Physical
    #        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0     <=== name, Physical
    # On my desktop running:
    """eno1      Link encap:Ethernet  HWaddr 00:22:4d:7c:4d:d9
          inet addr:192.168.1.23  Bcast:192.168.1.255  Mask:255.255.255.0
          inet6 addr: fe80::222:4dff:fe7c:4dd9/64 Scope:Link
          inet6 addr: 2601:602:9802:93a8:222:4dff:fe7c:4dd9/64 Scope:Global
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:133136736 errors:12 dropped:0 overruns:0 frame:12
          TX packets:63631643 errors:52831 dropped:0 overruns:0 carrier:52831
          collisions:32307027 txqueuelen:1000
          RX bytes:199455734537 (199.4 GB)  TX bytes:4384071947 (4.3 GB)
          Interrupt:20 Memory:f7900000-f7920000
"""



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
        assert ifconfig_lines[0][0] != " ", "Line 0 character 0 should not be a space, it should be the name of an"\
                "interface.  Line is \n{}".format(ifconfig_lines[0])
        name, flags_str, mtu_str, mtu_value = ifconfig_lines.split()
        # Insofar as I can tell, none of the other lines are required to be present.  There may be a better way to
        # figure this out, but I don't know enough yet. In particular, there may be several IPv6 addresses.
        # In https://bugs.launchpad.net/tempest/+bug/1381416, it shows that different systems have different output
        # formats, and this messes up tempest,
        # See also https://bugzilla.redhat.com/show_bug.cgi?id=784314
        ipv6_address_list = list()
        ipv4_address_list = list()
        for line in ifconfig_lines[1:]:
            fields = line.split()
            if fields[0] == "inet":
                ipv4_entry = collections.namedtuple("ip4_if_entry", ['ipv4_address', 'netmask', 'broadcast'] )
                ipv4_entry.ipv4_address = fields[1]
                assert fields[2]=='netmask', "Parsing error: fields[2] should be 'netmask' but is really "+fields[2] 
                ipv4_entry.netmask = fields[3]
                assert fields[4]=='broadcast', "Parsing error: fields[2] should be 'netmask' but is really "+fields[4] 
                ipv4_entry.broadcast = fields[5]
                ipv4_address_list.append(ipv4_entry)
            elif fields[0] == 'inet6' :
                ipv6_entry = collections.namedtuple("ipv6_entry", ['ipv6_address', 'prefixlen', 'scopeid' ] )
                ipv6_entry.ipv6_address = fields[1]
                assert fields[2] == 'prefixlen'
                ipv6_entry.prefixlen = fields[3]
                assert fields[4] == 'scopeid'
                ipv6_entry.scopeid = fields[5]
                ipv6_address_list.append(ipv6_entry)
            elif fields[0] == "ether" :
                # ether 00:21:6a:53:14:10  txqueuelen 1000  (Ethernet)
                mac_entry = collections.namedtuple('ether_entry', ['addr', 'txqueuelen', 'class'] )
                mac_entry.addr = fields[1]
                assert fields[2] == "txqueuelen"
                mac_entry.txqueuelen = fields[3]


            








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



if __name__ == "__main__" :
    interface =

    """jeffs@jeff-desktop:~/python/nbmdt (development)*$ ifconfig -a
eno1      Link encap:Ethernet  HWaddr 00:22:4d:7c:4d:d9  
          inet addr:192.168.1.23  Bcast:192.168.1.255  Mask:255.255.255.0
          inet6 addr: fe80::222:4dff:fe7c:4dd9/64 Scope:Link
          inet6 addr: 2601:602:9802:93a8:222:4dff:fe7c:4dd9/64 Scope:Global
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:131239939 errors:12 dropped:0 overruns:0 frame:12
          TX packets:62635737 errors:52414 dropped:0 overruns:0 carrier:52414
          collisions:31801476 txqueuelen:1000 
          RX bytes:196913568317 (196.9 GB)  TX bytes:4276747726 (4.2 GB)
          Interrupt:20 Memory:f7900000-f7920000 

enp3s0    Link encap:Ethernet  HWaddr 00:10:18:cc:9c:77  
          inet addr:192.168.3.50  Bcast:192.168.3.255  Mask:255.255.252.0
          inet6 addr: fe80::210:18ff:fecc:9c77/64 Scope:Link
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:16 errors:0 dropped:0 overruns:0 frame:0
          TX packets:2780 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:3520 (3.5 KB)  TX bytes:581009 (581.0 KB)
          Interrupt:18 

lo        Link encap:Local Loopback  
          inet addr:127.0.0.1  Mask:255.0.0.0
          inet6 addr: ::1/128 Scope:Host
          UP LOOPBACK RUNNING  MTU:65536  Metric:1
          RX packets:725637 errors:0 dropped:0 overruns:0 frame:0
          TX packets:725637 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1 
          RX bytes:44306038 (44.3 MB)  TX bytes:44306038 (44.3 MB)

lxcbr0    Link encap:Ethernet  HWaddr 00:16:3e:00:00:00  
          inet addr:10.0.3.1  Bcast:0.0.0.0  Mask:255.255.255.0
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

sit0      Link encap:IPv6-in-IPv4  
          NOARP  MTU:1480  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

vboxnet0  Link encap:Ethernet  HWaddr 0a:00:27:00:00:00  
          BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

vboxnet1  Link encap:Ethernet  HWaddr 0a:00:27:00:00:01  
          BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

vboxnet2  Link encap:Ethernet  HWaddr 0a:00:27:00:00:02  
          BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

vboxnet3  Link encap:Ethernet  HWaddr 0a:00:27:00:00:03  
          BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

virbr0    Link encap:Ethernet  HWaddr 52:54:00:2c:bc:48  
          inet addr:192.168.122.1  Bcast:192.168.122.255  Mask:255.255.255.0
          UP BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)

virbr0-nic Link encap:Ethernet  HWaddr 52:54:00:2c:bc:48  
          BROADCAST MULTICAST  MTU:1500  Metric:1
          RX packets:0 errors:0 dropped:0 overruns:0 frame:0
          TX packets:0 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:0 (0.0 B)  TX bytes:0 (0.0 B)
"""

