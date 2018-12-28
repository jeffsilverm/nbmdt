#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# A demonstration of what I can do with pyroute2, which uses netlink
# based on Evan's ramblings     http://www.fos.tech/posts/pyroute2-linux-networking-made-easy/
import datetime
import pprint  # We'll use this later
import socket
import time
import typing
from enum import Enum
import sys
# From https://stackoverflow.com/questions/16422507/python-is-a-given-network-interface-wifi-or-ethernet
from pyroute2 import IW
from pyroute2.netlink import NetlinkError


import pyroute2
from pyroute2 import IPDB
from pyroute2 import IPRoute

pp = pprint.PrettyPrinter(indent=3)


class NetlinkEvents(Enum):
    # A new neighbor has appeared
    RTM_NEWNEIGH = 'RTM_NEWNEIGH'
    # We're no longer watching a certain neighbor
    RTM_DELNEIGH = 'RTM_DELNEIGH'
    # A new network interface has been created
    RTM_NEWLINK = 'RTM_NEWLINK'
    # A network interface has been deleted
    RTM_DELLINK = 'RTM_DELLINK'
    # An IP address has been added to a network interface
    RTM_NEWADDR = 'RTM_NEWADDR'
    # An IP address has been deleted off of a network interface
    RTM_DELADDR = 'RTM_DELADDR'
    # A route has been added to the routing table
    RTM_NEWROUTE = 'RTM_NEWROUTE'
    # A route has been removed from the routing table
    RTM_DELROUTE = 'RTM_DELROUTE'
    # For a more complete list of messages, see the NetLink man page,
    # http://man7.org/linux/man-pages/man7/rtnetlink.7.html
    # RFC 3549  https://tools.ietf.org/html/rfc3549


the_current_time: datetime.datetime = datetime.datetime.now()


# define a watcher.  This method is going to be called when the netlink interface
# returns a message, such as when an IP address changes or a WiFi interface changes status
def new_address_callback(ipdb2, netlink_message, action):
    global the_current_time
    ping_time: datetime.datetime = datetime.datetime.now()
    print(ping_time, str(ipdb2), file=sys.stderr)

    print(f"At {the_current_time}, got a network messagem {action}")
    if action == NetlinkEvents.RTM_NEWADDR.name:
        print(f"The delta time is {ping_time - the_current_time}\n" + 50 * "$")
        if netlink_message['family'] == socket.AF_INET:
            netlink_message['family'] = "IPv4"
        elif netlink_message['family'] == socket.AF_INET6:
            netlink_message['family'] = "IPv6"
        else:
            print(f"WARNING: Unknown value of family: {netlink_message['family']}",
                  file=sys.stderr)
        pp.pprint(netlink_message['attrs'])
        print("The family is:", netlink_message['family'])
    else:
        print(f"Got a different action, {action}")
        pp.pprint(netlink_message)
    the_current_time = ping_time


# from https://docs.pyroute2.org/general.html
def routing_table() -> dict:
    # get access to the netlink socket
    global ip

    link_table = dict()  # dictionary of interface names, key'd by interface index
    links: typing.List[pyroute2.IPRoute] = ip.get_links()
    for link in links:
        link_attrs = link['attrs']
        link_index = link['index']
        assert isinstance(link_attrs, list),\
            f"link_attrs should be a list but is actually a {type(link_attrs)} of length {len(link_attrs)}"
        for attr in link_attrs:
            assert isinstance(attr,
                            pyroute2.netlink.nla_slot), f"attrs should be pyroute2.netlink.nla_slot but is really a " \
               f"{type(attr)}"
            if attr[0] == 'IFLA_IFNAME':
                link_table[link_index] = dict()
                link_table[link_index]['IFLA_IFNAME'] = attr[1]
            elif attr[0] == 'IFLA_AF_SPEC':
                link_table[link_index]['IFLA_AF_SPEC'] = attr[1]
                try:
                    ifstr = pp.pformat(link_table[link_index]['IFLA_AF_SPEC'])
                    print(f"Inteface {link_index} named {link_table[link_index]['IFLA_IFNAME']}",
                          "has IFLA_AF_SPEC:\n" + ifstr)
                except KeyError as k:
                    print(f"Raised KeyError on link_index {link_index} k is {k}", file=sys.stderr)
                else:
                    if attr[1]['attrs'][0][0] != 'AF_INET':
                        print(f"attr[1]['attrs'][0][0] should be AF_INET, is actually {attr[1]['attrs'][0][0]}",
                              file=sys.stderr)
                    if attr[1]['attrs'][1][0] != 'AF_INET6':
                        print(f"attr[1]['attrs'][0][0] should be AF_INET, is actually {attr[1]['attrs'][1][0]}",
                              file=sys.stderr)


# FYI: XDP is eXpress Data Path, see https://www.slideshare.net/lcplcp1/introduction-to-ebpf-and-xdp
    # Google XDP Benchmarks mlx4
    # BPF and XDP Reference guide https://cilium.readthedocs.io/en/v1.3/bpf/ However, that points to
    # https://cilium.readthedocs.io/en/v1.3/ which points to https://cilium.readthedocs.io/en/v1.3/install/guides/#mesos
    # which points to https://cilium.readthedocs.io/en/v1.3/configuration/metrics/ which points to
# https://prometheus.io/ and also
    # https://grafana.com/

    print_routing_table(links)
    return link_table


def print_routing_table(links) -> None:
    # print interfaces
    print(type(links), file=sys.stderr)
    for k in range(len(links)):
        link = links[k]
        print(f"{k} -------")
        pp.pprint(link)


if "__main__" == __name__:
    ip = IPRoute()
    ipdb = IPDB()
    link_tble = routing_table()
    # Set up the watcher
    addr_callback = ipdb.register_callback(new_address_callback)
    for i in range(1, 20):
        print(f"Sleeping {i} {the_current_time}", file=sys.stderr)
        time.sleep(1)

    # From https://stackoverflow.com/questions/16422507/python-is-a-given-network-interface-wifi-or-ethernet

    ipv4_def_route = ip.get_default_routes(family=socket.AF_INET)
    ipv4_def_route_str = pp.pformat(ipv4_def_route)
    print("IPv4 " + 40*'=' + "\n" + ipv4_def_route_str)
    ipv6_def_route = ip.get_default_routes(family=socket.AF_INET6)
    ipv6_def_route_str = pp.pformat(ipv6_def_route)
    print("IPv6 " + 40*'-' + "\n" + ipv6_def_route_str)
    iw = IW()
    index = ip.link_lookup(ifname=sys.argv[1])[0]
    try:
        iw.get_interface_by_ifindex(index)
        print("wireless interface")
    except NetlinkError as e:
        if e.code == 19:  # 19 'No such device'
            print("not a wireless interface")
    finally:
        iw.close()
        ip.close()

    ipdb.unregister_callback(addr_callback)
