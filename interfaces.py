#! /usr/bin/env python3
# -*- coding: utf-8 -*-


# netifaces will do everything I need and it is portable!  Actually, it won't do, it won't tell me
# there is a carrier or if the interface is up.  The ip command will.  But the ip command won't
# run oN windows.
import subprocess
import sys
from os import path as path
from pathlib import Path

import netifaces  # See /usr/lib/python3/dist-packages/netifaces-0.10.4.egg-info/PKG-INFO

from configuration import IP_COMMAND

# This should be a configuration file item - on ubuntu, the IP_COMMAND is
# /bin/ip .  So what I did was symlink it so that both /bin/ip and
# /usr/sbin/ip work.  But I can do that because I am a sysadmin.
# Issue 2 https://github.com/jeffsilverm/nbmdt/issues/2
# MARK ISSUE 2 as resolved, because I moved it to configuration.py
NET_DEVS_PATH = Path("/sys/class/net")


# There is another way to do it: use the /sys/class/net file tree:
# jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (blue-sky) *  $ ls /sys/class/net/eno1/statistics
# collisions  rx_compressed  rx_errors        rx_length_errors  rx_over_errors     tx_bytes           tx_dropped
#  tx_heartbeat_errors
# multicast   rx_crc_errors  rx_fifo_errors   rx_missed_errors  rx_packets         tx_carrier_errors  tx_errors
#  tx_packets
# rx_bytes    rx_dropped     rx_frame_errors  rx_nohandler      tx_aborted_errors  tx_compressed      tx_fifo_errors
#  tx_window_errors
# jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (blue-sky) *  $
# See https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-net


# There is an ip command cheat sheet at
# https://access.redhat.com/sites/default/files/attachments/rh_ip_command_cheatsheet_1214_jcs_print.pdf

def none_if_none(s):
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
    def get_all_physical_interfaces(cls) -> list:  # class PhysicalInterface
        """
        This method returns a list of interfaces as known by the netifaces package
        """

        links_list: list = netifaces.interfaces()
        return links_list

    def run_ip_link_command(self, interface=None) -> dict:
        """
        This method returns all of the properties of the interface interface as
        a dictionary which is keyed by interface name and has the value of a
        dictionary of properties, keyed by prop name
        If interface is None, then return the properties of all interfaces as a
        dictionary.
        Given the overhead of forking a subprocess, does it make sense to run this
        for a single interface or run this for all interfaces all the time and
        just return the desired interface?

        :return:
        """
        interfaces_dict = dict()
        if interface is not None:
            completed = subprocess.run(
                [IP_COMMAND, "--details", "--oneline", "link", "list"], stdin=None,
                input=None,
                stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None,
                check=False)
        else:
            completed = subprocess.run(
                [IP_COMMAND, "--details", "--oneline", "link", "show", "dev", interface], stdin=None,
                input=None,
                stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None,
                check=False)
        completed_str = completed.stdout.decode('ascii')
        # The output of the ip link command looks like:
        r"""
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
        r"""
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (blue-sky) *  $ ip --oneline --detail link list eno1
3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP mode DEFAULT group default qlen 1000\   
 link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 
 gso_max_size 65536 gso_max_segs 65535 
jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (blue-sky) *  $ 

        """
        # Get rid of the \ characters.  They really are in there
        completed_str = completed_str.replace("\\", "")
        lines_lst = completed_str.split()
        for line in lines_lst:
            link_fields = line.split()
            # skip the line number, link_fields[0]
            interface_name = link_fields[1]
            # According to https://pypi.org/project/ifparser/ , the possible values
            # of interface_flags include:
            # BROADCAST, LOOPBACK, MULTICAST, RUNNING, UP, DYNAMIC, NOARP, PROMISC, POINTOPOINT, SIMPLEX, SMART,
            # MASTER, SLAVE
            # How do they know that?

            interface_flags = link_fields[2]
            property_dict = {}
            for field_idx in range(2, len(link_fields), 2):
                property_name = link_fields[field_idx]
                property_value = link_fields[field_idx + 1]
                property_dict[property_name] = property_value
            for if_flag in ["BROADCAST", "LOOPBACK", "MULTICAST", "RUNNING",
                            "UP", "DYNAMIC", "NOARP", "PROMISC", "POINTOPOINT", "SIMPLEX",
                            "SMART", "MASTER", "SLAVE"]:
                property_dict[if_flag] = if_flag in interface_flags
            interface_obj = self.__init__(interface_name, property_dict)
            interfaces_dict[interface_name] = interface_obj
        return interfaces_dict

    @staticmethod
    def link_properties(ifname: str) -> dict:
        """
        Return a dictionary of properties, keyed by prop name and the
        value of that prop.  THIS IS HIGHLY *NOT* PORTABLE - IT WILL ONLY
        RUN ON LINUX"

        :param ifname:  The name of the interface to report
        :return:    A dictionary of properties of the interface
        """

        properties = dict()
        assert path.exists(str(NET_DEVS_PATH)), \
            f"The networks device path {NET_DEVS_PATH} does not exist." \
            "This is a serious internal software error." \
            "Please submit a bug report and include the results of the" \
            "\nls -lR /sys\ncommand"
        dev_properties_path = NET_DEVS_PATH / ifname
        if not path.exists(str(dev_properties_path)):
            print(
                f"The device path {str(dev_properties_path)} does not exist.  " 
                f"It likely that the directory for the interface named {ifname} does not exist.\n",
                "The devices that are known are:", file=sys.stderr)
            for f in dev_properties_path.glob("*"):
                print(f, file=sys.stderr)
            raise AssertionError(
                f"Inteface {ifname} not found in pseudo file system")
        for d in dev_properties_path.glob("*"):
            if d.is_dir():
                continue
            gh = str(d)
            prop = gh[gh.rindex("/") + 1:]
            with open(gh, "rb") as fp:
                contents = None  # Fallback value if fp.readlines raises an error
                try:
                    contents = fp.readlines()
                except OSError as o:
                    print(f"Property {prop} cannot be known due to OSError {str(o)}", file=sys.stderr)
                    continue
                except UnicodeDecodeError as u:
                    print(f"Property {prop} in {gh} raised a UnicodeDecodeError {str(u)}", file=sys.stderr)
                properties[prop] = contents
        return properties


if "__main__" == __name__:
    all_interfaces = PhysicalInterface.get_all_physical_interfaces()
    for i_f in all_interfaces:
        print(i_f)
