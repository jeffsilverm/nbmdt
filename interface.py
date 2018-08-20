#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

import collections
import os
import subprocess
import sys
from platform import system
from typing import Union

from constants import ErrorLevels
from layer import Layer
from utilities import OsCliInter




#

def none_if_none(s):
    return s if s is not None else "None"


class Interface(Layer):
    """
    Methods for dealing with interfaces.  An "interface" for the purposes of this program
    is a combination of the physical and data link layers in the OSI model, and the
    network access layer in the TCP/IP model
    """

    # The location of the command to get the interface information is OS specific and common
    # across all interfaces, so it is a class variable
    if 'Linux' == OsCliInter.system:
        # The command to get network access information from the OS.  I suppose it could be in /sbin or /usr/sbin
        if os.path.isfile("/bin/ip"):
            IP_COMMAND = "/bin/ip"
        elif os.path.isfile("/usr/bin/ip"):
            IP_COMMAND = "/usr/bin/ip"
        else:
            raise FileNotFoundError("Could not find the ip command, not in /bin/ip nor in /usr/bin/ip")
        # the ip link list command instead of the ip link show DEV command
        # For a complete list of flags and parameters, see
        # http://man7.org/linux/man-pages/man7/netdevice.7.html
        discover_command = [IP_COMMAND, "--details", "--oneline", "link", "list"]
    elif 'Windows' == OsCliInter.system:
        discover_command = None
        raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
    elif 'Mac OS' == OsCliInter.system:
        discover_command = None
        raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
    else:
        discover_command = None
        raise ValueError(f"System is {OsCliInter.system} and I don't recognize it")

    def __init__(self, if_name, state_up, broadcast, lower_up, carrier, multicast,
                 mtu, qdisc, qlen, state, link_addr, broadcast_addr, mode = "DEFAULT", **kwargs ):
        self.layer = super()
        self.if_name = if_name
        assert type(state_up) == bool, f"state_up is {type(state_up)}"
        self.state_up = state_up
        self.broadcast = broadcast
        self.lower_up = lower_up
        self.carrier = carrier
        self.multicast = multicast
        self.mtu = mtu
        self.qdisc = qdisc
        self.state = state
        self.mode = mode
        self.qlen = qlen
        self.link_addr = link_addr
        self.broadcast_addr = broadcast_addr
        for k in kwargs:
            self.__setattr__(k, kwargs[k])


    def discover(self):
        """
        Call this method to discover all of the interfaces in the system.  This command
        will call the command line command to list all of the interfaces
        :return: a dictionary of Interface objects, keyed by interface name
        """


        # Did the caller specify a string with the description of the interface?  That might be if the caller called

        get_details_command = [self.IP_COMMAND, "--details", "--oneline", "link", "show"]

        if lnk_str is None and self.my_os == 'Linux':
            command: list = self.get_details_command.append(name)
            lnk_str: str = OsCliInter.run_command(command)
        fields = lnk_str.split()
        # fields[0] is the line number, skip that.  fields[1] is the device name
        self.name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
        flags = fields[2]
        self.state_up = "UP" in flags
        self.broadcast = "BROADCAST" in flags
        self.lower_up = "LOWER_UP" in flags
        self.carrier = "NO-CARRIER" not in flags
        self.multicast = "MULTICAST" in flags


        for idx in range(3, len(fields) - 1, 2):
            # Accortding to http://lartc.org/howto/lartc.iproute2.explore.html , qdisc stands for "Queueing
            # Discipline" and it's vital.
            self.__setattr__(fields[idx], fields[idx + 1])

    def get_status(self) -> ErrorLevels:
        return self.layer.get_status()

    @classmethod
    def discover(cls):
        """
        Discover all of the interfaces on this machine

        :return:    a dictionary of interfaces, key'd by name.  The value is an Interface object
        """

        completed_str = OsCliInter.run_command(cls.discover_command)
        links_list = completed_str.split('\n')
        link_dict = dict()
        for lnk in links_list:
            if len(lnk) == 0:  # there may be an empty trailing line in the output
                break
            fields = completed_str.split()
            # fields[0] is the line number, skip that.  fields[1] is the device name
            intf_name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
            link_dict[intf_name] = Interface(intf_name, lnk)

        return link_dict


# Rename this class to Interface
class PhysicalInterface(Interface):
    def __init__(self, intf_name, intf_description: Union[str, list]):
        self.intf_name = intf_name
        if isinstance(intf_description, list):
            self.intf_description = intf_description.copy()

    def __str__(self):
        s = "name: " + self.intf_name
        for key in self.intf_description.keys():
            s += "\t" + key + ": " + self.intf_description[key]

        return s

    @classmethod
    def get_all_physical_interfaces(self):
        """This method returns a dictionary of interfaces as known by the ip link list command
        """

        completed = subprocess.run(
            print("get_all_physical_interfaces works for linux, nothing else", file=sys.stderr)
            [self.IP_COMMAND, "--details", "--oneline", "link", "list"], stdin=None,
            input=None,
            stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None,
            check=False)
        completed_str = completed.stdout.decode('ascii')
        """
jeffs@jeffs-desktop:~/nbmdt (blue-sky)*$ ip --oneline --detail link list
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000\    
link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00 promiscuity 0 addrgenmode eui64 numtxqueues 1 numrxqueues 1 
gso_max_size 65536 gso_max_segs 65535 
2: enp3s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN mode DEFAULT group default qlen 1000\    
link/ether 00:10:18:cc:9c:77 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 5 numrxqueues 5 
gso_max_size 65536 gso_max_segs 65535 
3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000\   
 link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 
 gso_max_size 65536 gso_max_segs 65535 
4: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 
1000\    link/ether 52:54:00:ef:47:ed brd ff:ff:ff:ff:ff:ff promiscuity 0 \    bridge forward_delay 200 hello_time 
200 max_age 2000 ageing_time 30000 stp_state 1 priority 32768 vlan_filtering 0 vlan_protocol 802.1Q bridge_id 
8000.52:54:0:ef:47:ed designated_root 8000.52:54:0:ef:47:ed root_port 0 root_path_cost 0 topology_change 0 
topology_change_detected 0 hello_timer    1.73 tcn_timer    0.00 topology_change_timer    0.00 gc_timer  138.73 
vlan_default_pvid 1 group_fwd_mask 0 group_address 01:80:c2:00:00:00 mcast_snooping 1 mcast_router 1 
mcast_query_use_ifaddr 0 mcast_querier 0 mcast_hash_elasticity 4 mcast_hash_max 512 mcast_last_member_count 2 
mcast_startup_query_count 2 mcast_last_member_interval 100 mcast_membership_interval 26000 mcast_querier_interval 
25500 mcast_query_interval 12500 mcast_query_response_interval 1000 mcast_startup_query_interval 3124 
nf_call_iptables 0 nf_call_ip6tables 0 nf_call_arptables 0 addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 
65536 gso_max_segs 65535 
5: virbr0-nic: <BROADCAST,MULTICAST> mtu 1500 qdisc pfifo_fast master virbr0 state DOWN mode DEFAULT group default 
qlen 1000\    link/ether 52:54:00:ef:47:ed brd ff:ff:ff:ff:ff:ff promiscuity 1 \    tun \    bridge_slave state 
disabled priority 32 cost 100 hairpin off guard off root_block off fastleave off learning on flood on port_id 0x8001 
port_no 0x1 designated_port 32769 designated_cost 0 designated_bridge 8000.52:54:0:ef:47:ed designated_root 
8000.52:54:0:ef:47:ed hold_timer    0.00 message_age_timer    0.00 forward_delay_timer    0.00 topology_change_ack 0 
config_pending 0 proxy_arp off proxy_arp_wifi off mcast_router 1 mcast_fast_leave off mcast_flood on addrgenmode none 
numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
6: lxcbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 
1000\    link/ether 00:16:3e:00:00:00 brd ff:ff:ff:ff:ff:ff promiscuity 0 \    bridge forward_delay 1500 hello_time 
200 max_age 2000 ageing_time 30000 stp_state 0 priority 32768 vlan_filtering 0 vlan_protocol 802.1Q bridge_id 
8000.0:16:3e:0:0:0 designated_root 8000.0:16:3e:0:0:0 root_port 0 root_path_cost 0 topology_change 0 
topology_change_detected 0 hello_timer    0.00 tcn_timer    0.00 topology_change_timer    0.00 gc_timer  138.72 
vlan_default_pvid 1 group_fwd_mask 0 group_address 01:80:c2:00:00:00 mcast_snooping 1 mcast_router 1 
mcast_query_use_ifaddr 0 mcast_querier 0 mcast_hash_elasticity 4 mcast_hash_max 512 mcast_last_member_count 2 
mcast_startup_query_count 2 mcast_last_member_interval 100 mcast_membership_interval 26000 mcast_querier_interval 
25500 mcast_query_interval 12500 mcast_query_response_interval 1000 mcast_startup_query_interval 3124 
nf_call_iptables 0 nf_call_ip6tables 0 nf_call_arptables 0 addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 
65536 gso_max_segs 65535 
        """
        links_list = completed_str.split('\n')
        link_db = dict()
        for link in links_list:
            if len(
                    link) == 0:  # there may be an empty trailing line in the output
                break
            fields = link.split()
            intf_description = collections.OrderedDict()
            # fields[0] is the line number, skip that.  fields[1] is the device name
            intf_name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
            # fields[2] is the flags, see https://github.com/torvalds/linux/blob/master/include/uapi/linux/if.h
            intf_description['flags'] = fields[2]
            # Issue 1 https://github.com/jeffsilverm/nbmdt/issues/1
            for idx in range(3, len(fields) - 1, 2):
                # Accortding to http://lartc.org/howto/lartc.iproute2.explore.html , qdisc stands for "Queueing
                # Discipline" and it's vital.
                intf_description[fields[idx]] = fields[idx + 1]
            link_db[intf_name] = PhysicalInterface(intf_name, intf_description)

        return link_db


# There should be a class method here that contains a dictionary of all of the PhysicalInterfaces

# Move this class to network.py
class LogicalInterface(Interface):
    """Logical links have IPv4 and IPv6 addresses associated with them as known by the ip addr list command

    """

    logical_link_db: dict = dict()

    # Re-write this as PhysicalInterface does it, with the addr_name as a field and then a description which is a
    # dictionary.
    def __init__(self, addr_name, addr_family, addr_addr, addr_descr):
        """This creates a logical interface object.
        :param  addr_name   The name of this logical interface
        :param  addr_family "inet" or "inet6"
        :param  addr_addr   The IPv4 address if addr_family is "inet" or the IPv6 address if addr_family is "inet6"
        :param  addr_descr  The rest of the description of this logical address.
        """
        # Some sample returns - use these to figure out how to decode things
        """
1: lo    inet 127.0.0.1/8 scope host lo\       valid_lft forever preferred_lft forever
1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever
3: eno1    inet 192.168.0.16/24 brd 192.168.0.255 scope global dynamic eno1\       valid_lft 77480sec preferred_lft 
77480sec
3: eno1    inet6 2602:61:7e44:2b00:da69:ad33:274d:7a08/64 scope global noprefixroute \       valid_lft forever 
preferred_lft forever
3: eno1    inet6 fd00::f46d:ccdd:58aa:b371/64 scope global noprefixroute \       valid_lft forever preferred_lft forever
3: eno1    inet6 fe80::a231:e482:ec02:f75e/64 scope link \       valid_lft forever preferred_lft forever
4: virbr0    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0\       valid_lft forever preferred_lft 
forever
6: lxcbr0    inet 10.0.3.1/24 scope global lxcbr0\       valid_lft forever preferred_lft forever
jeffs@jeffs-desktop:/home/jeffs  $ 
"""
        super()
        self.addr_name = addr_name
        if addr_family != "inet" and addr_family != "inet6":
            raise ValueError(
                "misunderstood value of addr_family: {}".format(addr_family))
        self.addr_family = addr_family
        self.addr_addr = addr_addr
        # For IPv4, scope is either host or global
        # For IPv6, scope is either host, link, or global.  However, the wikipedia
        # article on IPv6 doesn't mention host scope.  ULAs are global.
        self.scope = addr_descr["scope"]
        for key in addr_descr.keys():
            setattr(self, key, addr_descr[key])
        if not hasattr(self, 'broadcast'):
            self.broadcast = None

    """def __str__(self):
        s = "name: " + self.addr_name + '\t'
        s += "family:" + self.addr_family + '\t'
        s += "address: " + self.addr_addr + '\t'
        if self.addr_family == "inet6":
            s += ("scope: " + none_if_None(self.scope) + "\t")
        else:
            s += ("broadcast: " + none_if_None(self.broadcast) + "\t")
        return s"""

    @classmethod
    def get_all_logical_interfaces(self):
        """This method returns a dictionary, keyed by name, of logical interfaces as known by the ip address list
        command.  Note that if a physical link does not an IPv4 address or an IPv6 address, then the ip command doesn't
        show it.  If a physical link has an IPv4 address and an IPv6 address, then there will be 2 entries"""
        IP_COMMAND = "/usr/bin/ip"
        completed = subprocess.run([self.IP_COMMAND, "--oneline", "address", "list"],
                                   stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None,
                                   shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        """
        jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development) *  $ ip --oneline address list
1: lo    inet 127.0.0.1/8 scope host lo\       valid_lft forever preferred_lft forever
1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever
3: eno1    inet 192.168.0.16/24 brd 192.168.0.255 scope global dynamic eno1\       valid_lft 63655sec preferred_lft 
63655sec
3: eno1    inet6 2602:61:7e44:2b00:da69:ad33:274d:7a08/64 scope global noprefixroute \       valid_lft forever 
preferred_lft forever
3: eno1    inet6 fd00::f46d:ccdd:58aa:b371/64 scope global noprefixroute \       valid_lft forever preferred_lft forever
3: eno1    inet6 fe80::a231:e482:ec02:f75e/64 scope link \       valid_lft forever preferred_lft forever
4: virbr0    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0\       valid_lft forever preferred_lft 
forever
6: lxcbr0    inet 10.0.3.1/24 scope global lxcbr0\       valid_lft forever preferred_lft forever
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development) *  $ 

        """
        # addrs_list is really a list of logical interfaces
        addrs_list = completed_str.split('\n')
        addr_db = dict()
        for addr in addrs_list:
            # addrs_list usually but not always has an empty element at the end
            if len(addr) == 0:
                break
            # https://docs.python.org/3/library/collections.html#collections.OrderedDict
            # ad is an attribute dictionary.  The string returned by the ip command will look like:
            # 3: wlp12s0    inet 10.5.66.10/20 brd 10.5.79.255 scope global dynamic wlp12s0\       valid_lft 85452sec
            #  preferred_lft 85452sec
            # addr_desc is a further description of an an address
            addr_desc = collections.OrderedDict()
            fields = addr.split()
            addr_name = fields[1]  # Field 0 is a number, skip it
            addr_family = fields[2]  # Either inet or inet6
            assert addr_family == "inet" or addr_family == "inet6"
            addr_addr = fields[3]  # Either IPv4 or IPv6 address
            # All of the rest of strings in the ip addr list command are in the
            # of key value pairs, delimited by spaces
            for idx in range(4, len(fields) - 1, 2):
                # Because addr_desc is an ordered dictionary, the results will always be output in the same order
                addr_desc[fields[idx]] = fields[idx + 1]
            # A single logical interface can have several addresses and several families
            # so the logical interface name is a key to a value which is a list
            # of addresses.
            if addr_name not in addr_db:
                # addr_name, addr_family, addr_addr, scope=None, broadcast=None, remainder=None
                """
                    def __init__(self, addr_name, addr_family, addr_addr, addr_descr ):
                """
                addr_db[addr_name] = [LogicalInterface(addr_name=addr_name,
                                                       addr_family=addr_family,
                                                       addr_addr=addr_addr,
                                                       addr_descr=addr_desc)]
            else:
                addr_db[addr_name].append(LogicalInterface(addr_name=addr_name,
                                                           addr_family=addr_family,
                                                           addr_addr=addr_addr,
                                                           addr_descr=addr_desc))
        return addr_db


if __name__ == "__main__":
    # nominal = SystemDescription.describe_current_state()

    # Create a dictionary, keyed by link name, of the physical interfaces
    link_db = PhysicalInterface.get_all_physical_interfaces()
    # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
    addr_db = LogicalInterface.get_all_logical_interfaces()

    print("links ", '*' * 40)
    for link in link_db.keys():
        link_int_descr = link_db[link].intf_description
        mac_addr = link_int_descr['link/ether'] if 'link/ether' in \
                                                   link_int_descr else "00:00:00:00:00:00"
        print(link, mac_addr, link_int_descr['state'])

    print("Addresses ", '*' * 40)
    for addr_name in addr_db:
        print("\n{}\n".format(addr_name))
        for addr in addr_db[addr_name]:  # The values of the addr_db are descriptions of addresses
            assert isinstance(addr, LogicalInterface)
            print("   " + str(addr))
