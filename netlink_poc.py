#! /usr/bin/python3
# -*- coding: utf-8 -*-
#
# A demonstration of what I can do with pyroute2, which uses netlink
# based on Evan's ramblings     http://www.fos.tech/posts/pyroute2-linux-networking-made-easy/
import datetime
import pprint  # We'll use this later
import sys
import time
import socket
from enum import Enum

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
    if action == NetlinkEvents.RTM_NEWADDR.name:
        ping_time: datetime.datetime = datetime.datetime.now()
        print(ping_time - the_current_time)
        if netlink_message['family'] == socket.AF_INET:
            netlink_message['family'] = "IPv4"
        elif netlink_message['family'] == socket.AF_INET6:
            netlink_message['family'] = "IPv6"
        else:
            pass
        pp.pprint(netlink_message['attrs']+"\n"+netlink_message['family'])
        the_current_time = ping_time
        print(the_current_time, ipdb2, file=sys.stderr)


# from https://docs.pyroute2.org/general.html
def print_routing_table() -> None:
    # get access to the netlink socket
    ip = IPRoute()

    # print interfaces
    links = ip.get_links()
    print(type(links), file=sys.stderr)
    for k in range(len(links)):
        link = links[k]
        print(f"{k} -------")
        pp.pprint(link)


if "__main__" == __name__:
    print_routing_table()
    ipdb = IPDB()
    # Set up the watcher
    addr_callback = ipdb.register_callback(new_address_callback)
    for i in range(1, 20):
        print(f"Sleeping {i} {the_current_time}", file=sys.stderr)
        time.sleep(1)

    ipdb.unregister_callback(addr_callback)
