#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import subprocess
import sys

# This should be a configuration file item
IP_COMMAND = "/bin/ip"


# There is an ip command cheat sheet at https://access.redhat.com/sites/default/files/attachments/rh_ip_command_cheatsheet_1214_jcs_print.pdf

def none_if_None(s):
    return s if s is not None else "None"


class PhysicalInterface(object):
    def __init__(self, intf_name, intf_description):
        self.intf_name = intf_name
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
            [IP_COMMAND, "--details", "--oneline", "link", "list"], stdin=None,
            input=None,
            stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None,
            check=False)
        completed_str = completed.stdout.decode('ascii')
        """
jeffs@jeffs-desktop:~/nbmdt (blue-sky)*$ ip --oneline --detail link list
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000\    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00 promiscuity 0 addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
2: enp3s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN mode DEFAULT group default qlen 1000\    link/ether 00:10:18:cc:9c:77 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 5 numrxqueues 5 gso_max_size 65536 gso_max_segs 65535 
3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
4: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 1000\    link/ether 52:54:00:ef:47:ed brd ff:ff:ff:ff:ff:ff promiscuity 0 \    bridge forward_delay 200 hello_time 200 max_age 2000 ageing_time 30000 stp_state 1 priority 32768 vlan_filtering 0 vlan_protocol 802.1Q bridge_id 8000.52:54:0:ef:47:ed designated_root 8000.52:54:0:ef:47:ed root_port 0 root_path_cost 0 topology_change 0 topology_change_detected 0 hello_timer    1.73 tcn_timer    0.00 topology_change_timer    0.00 gc_timer  138.73 vlan_default_pvid 1 group_fwd_mask 0 group_address 01:80:c2:00:00:00 mcast_snooping 1 mcast_router 1 mcast_query_use_ifaddr 0 mcast_querier 0 mcast_hash_elasticity 4 mcast_hash_max 512 mcast_last_member_count 2 mcast_startup_query_count 2 mcast_last_member_interval 100 mcast_membership_interval 26000 mcast_querier_interval 25500 mcast_query_interval 12500 mcast_query_response_interval 1000 mcast_startup_query_interval 3124 nf_call_iptables 0 nf_call_ip6tables 0 nf_call_arptables 0 addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
5: virbr0-nic: <BROADCAST,MULTICAST> mtu 1500 qdisc pfifo_fast master virbr0 state DOWN mode DEFAULT group default qlen 1000\    link/ether 52:54:00:ef:47:ed brd ff:ff:ff:ff:ff:ff promiscuity 1 \    tun \    bridge_slave state disabled priority 32 cost 100 hairpin off guard off root_block off fastleave off learning on flood on port_id 0x8001 port_no 0x1 designated_port 32769 designated_cost 0 designated_bridge 8000.52:54:0:ef:47:ed designated_root 8000.52:54:0:ef:47:ed hold_timer    0.00 message_age_timer    0.00 forward_delay_timer    0.00 topology_change_ack 0 config_pending 0 proxy_arp off proxy_arp_wifi off mcast_router 1 mcast_fast_leave off mcast_flood on addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
6: lxcbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN mode DEFAULT group default qlen 1000\    link/ether 00:16:3e:00:00:00 brd ff:ff:ff:ff:ff:ff promiscuity 0 \    bridge forward_delay 1500 hello_time 200 max_age 2000 ageing_time 30000 stp_state 0 priority 32768 vlan_filtering 0 vlan_protocol 802.1Q bridge_id 8000.0:16:3e:0:0:0 designated_root 8000.0:16:3e:0:0:0 root_port 0 root_path_cost 0 topology_change 0 topology_change_detected 0 hello_timer    0.00 tcn_timer    0.00 topology_change_timer    0.00 gc_timer  138.72 vlan_default_pvid 1 group_fwd_mask 0 group_address 01:80:c2:00:00:00 mcast_snooping 1 mcast_router 1 mcast_query_use_ifaddr 0 mcast_querier 0 mcast_hash_elasticity 4 mcast_hash_max 512 mcast_last_member_count 2 mcast_startup_query_count 2 mcast_last_member_interval 100 mcast_membership_interval 26000 mcast_querier_interval 25500 mcast_query_interval 12500 mcast_query_response_interval 1000 mcast_startup_query_interval 3124 nf_call_iptables 0 nf_call_ip6tables 0 nf_call_arptables 0 addrgenmode eui64 numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
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


class LogicalInterface(object):
    """Logical links have IPv4 and IPv6 addresses associated with them as known by the ip addr list command

    """

    logical_link_db = dict()

    # Re-write this as PhysicalInterface does it, with the addr_name as a field and then a description which is a
    # dictionary.
    def __init__(self, addr_name, addr_family, addr_addr, addr_descr,
                 scope=None, broadcast=None, remainder=None):
        """This creates a logical interface object."""
        if addr_family != "inet" and addr_family != "inet6":
            raise ValueError(
                "misunderstood value of addr_family: {}".format(addr_family))
        self.addr_name = addr_name
        self.addr_family = addr_family
        self.addr_addr = addr_addr
        self.addr_descr = addr_descr
        # I have to have a better understanding of the symantecs of scope and
        # broadcast
        if ( ( scope is None ) + ( broadcast is None) ) != 1:  # True + True =
        #  2, True + False == False + True == 1, False + False == 0
            print(
                "While instantiating {}, ".format(addr_name),
                "One and only one of scope or broadcast must be None\n" \
                "scope is {} broadcast is {}\n".format(str(scope),
                                                       str(broadcast)),
                file=sys.stderr)
        self.scope = scope
        self.broadcast = broadcast
        self.remainder = remainder

    def __str__(self):
        s = "name: " + self.addr_name + '\t'
        s += "family:" + self.addr_family + '\t'
        s += "address: " + self.addr_addr + '\t'
        if self.addr_family == "inet6":
            s += ("scope: " + none_if_None(self.scope) + "\t")
        else:
            s += ("broadcast: " + none_if_None(self.broadcast) + "\t")
        s += "Remainder: " + none_if_None(self.remainder) + "\t"
        return s

    @classmethod
    def get_all_logical_link_addrs(cls):
        """This method creates a dictionary, keyed by name, of all of the (logical) links that have addresses.
        Since an interface can, and probably will, have more than one address, the values of this dictionary
        will be dictionaries keyed by address which will contain a description of the address"""

        completed = subprocess.run(
            [IP_COMMAND, "--details", "--oneline", "addr", "list"], stdin=None,
            input=None,
            stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None,
            check=False)
        completed_str = completed.stdout.decode('ascii')
        addrs_list = completed_str.split('\n')
        for line in addrs_list:
            """
jeffs@jeffs-laptop:~/nbmdt (development)*$ /usr/sbin/ip --oneline --detail 
addr show
1: lo    inet 127.0.0.1/8 scope host lo\       valid_lft forever preferred_lft forever
1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever
3: wlp12s0    inet 10.1.10.146/24 brd 10.1.10.255 scope global dynamic wlp12s0\       valid_lft 597756sec preferred_lft 597756sec
3: wlp12s0    inet6 fc00::1:2/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 2618::1/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 ff::1/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 fe80::5839:4589:a697:f8fd/64 scope link \       valid_lft forever preferred_lft forever
4: virbr0    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0\       valid_lft forever preferred_lft forever
jeffs@jeffs-laptop:~/nbmdt (development)*$

            """
            # if family is inet, then brd_scope is brd (broadcast) and brd_scope_val is the the broadcast IPv4 address
            # if family is inet6, then brd_scope is scope\ and brd_scope_val is either host, link, or global
            idx, link_name, family, addr_mask, brd_scope, brd_scope_val, remainder = line.split()
            logical_link_descr = cls.__init__(addr_name=link_name,
                                              addr_family=family,
                                              addr_addr=addr_mask,
                                              scope=(
                                              brd_scope if family == "inet" else None),
                                              broadcast=(
                                              None if family == "inet" else brd_scope),
                                              )
            cls.logical_link_db[link_name] = logical_link_descr

    @classmethod
    def get_all_logical_interfaces(self):
        """This method returns a dictionary, keyed by name, of logical interfaces as known by the ip address list
        command.  Note that if a physical link does not an IPv4 address or an IPv6 address, then the ip command doesn't
        show it.  If a physical link has an IPv4 address and an IPv6 address, then there will be 2 entries"""

        completed = subprocess.run([IP_COMMAND, "--oneline", "address", "list"],
                                   stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None,
                                   shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        # addrs_list is really a list of logical interfaces
        addrs_list = completed_str.split('\n')
        addr_db = dict()
        for addr in addrs_list:
            # addrs_list usually but not always has an empty element at the end
            if len(addr) == 0:
                break
            # https://docs.python.org/3/library/collections.html#collections.OrderedDict
            # ad is an attribute dictionary.  The string returned by the ip command will look like:
            # 3: wlp12s0    inet 10.5.66.10/20 brd 10.5.79.255 scope global dynamic wlp12s0\       valid_lft 85452sec preferred_lft 85452sec
            ad = collections.OrderedDict()
            fields = addr.split()
            addr_name = fields[1]

            addr_family = fields[2]  # Either inet or inet6
            assert addr_family == "inet" or addr_family == "inet6"
            addr_addr = fields[3]
            for idx in range(4, len(fields) - 1, 2):
                # Because ad is an ordered dictionary, the results will always be output in the same order
                ad[fields[idx]] = fields[idx + 1]
            # A single logical interface can have several addresses and several families
            # so the logical interface name is a key to a value which is a list
            # of addresses.
            if addr_name not in addr_db:
                # addr_name, addr_family, addr_addr, scope=None, broadcast=None, remainder=None
                addr_db[addr_name] = [LogicalInterface(addr_name=addr_name,
                                                       addr_family=addr_family,
                                                       addr_addr=addr_addr,
                                                       addr_descr=ad)]
            else:
                addr_db[addr_name].append(LogicalInterface(addr_name=addr_name,
                                                           addr_family=addr_family,
                                                           addr_addr=addr_addr,
                                                           addr_descr=ad))
        return addr_db


if __name__ == "__main__":
    # nominal = SystemDescription.describe_current_state()

    # Create a dictionary, keyed by link name, of the physical interfaces
    link_db = PhysicalInterface.get_all_physical_interfaces()
    # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
    addr_db = LogicalInterface.get_all_logical_interfaces()

    print("links ", '*' * 40)
    for link in link_db.keys():
        link_int_descr=link_db[link].intf_description
        mac_addr = link_int_descr['link/ether'] if 'link/ether' in \
                                                   link_int_descr else "00:00:00:00:00:00"
        print(link, mac_addr, link_int_descr['state'] )

    print("Addresses ", '*' * 40)
    for addr_name in addr_db:
        print("\n{}\n".format(addr_name))
        for addr in addr_db[addr_name]:  # The values of the addr_db are descriptions of addresses
            assert isinstance(addr, LogicalInterface)
            print("   " + str(addr))
