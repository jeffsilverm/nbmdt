#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Uses pyroute2, https://pypi.org/project/pyroute2/,
# to get the information it needs
import pprint
from socket import AF_INET, AF_INET6
from typing import Union

from pyroute2 import IPRoute

pp = pprint.PrettyPrinter(indent=4, width=20)


# From https://www.geeksforgeeks.org/python-convert-list-tuples-dictionary/
def convert(tup):
    """
    :param tup: Union[tuple, dict]: either a list of tuples or a dictionary where the values are either a tuple or a list
        of tuples:
    :return: dict: where the values are either lists of dictionaries or scalars
    """

    if isinstance(tup, dict):
        for k1 in tup.keys():
            if isinstance(tup[k1], tuple):
                tup[k1]: dict = convert(tup[k1])
    di = dict(tup)
    # recursively search for lists of tuples.
    for k1 in di.keys():
        if isinstance(di[k1], list):
            di[k1] = convert(di[k1])
    return di


tups = [("akash", [("inner_1", 1), ("inner_2", 2), ("inner_3", 3), ("inner_4",
                                                                    [("in_in_1", 1), ("in_in_2", 2)]), ("inner_5", 5)]),
        ("gaurav", 12), ("anand", 14), ("dict", {"d1": 'a', "d2": 'b', "d3": 'c'}),
        ("suraj", 20), ("akhil", 25), ("ashish", 30)]
c = convert(tups)
print(c)
pass

# get access to the netlink socket
ip = IPRoute()

# no monitoring here -- thus no bind()

# print interfaces.  This should go in interface.py
link_table = dict()  # link properties key'd by link name
addr_table = dict()  # link address information key'd by link name
# Links will have more than 1 address: at least an IPv4
# and an IPv6 address, but perhaps even more than that
links = ip.get_links()
for link in links:
    print(link)
    interface_name: Union[None, str] = None  # to guarantee that a KeyError Exception is raised
    for attr in link['attrs']:
        print("  ", attr)
        if attr[0] == 'IFLA_IFNAME':
            interface_name: str = attr[1]
            link_table[interface_name] = dict()  # Create an empty link table entry
        elif attr[0] == 'IFLA_AF_SPEC':
            print(f"--- printing the addresses? ---{interface_name}")
            for af_attr in attr[1]['attrs']:
                print(af_attr)
                for af1 in sorted(af_attr[1].keys()):
                    print(f"....{af1}: {af_attr[1][af1]}")
                    if isinstance(af_attr[1][af1], dict):
                        for k in sorted(af_attr[1][af1]):
                            print(f"{interface_name},,,,,,,,{k}: {af_attr[1][af1][k]}")
                pass
        else:
            link_table[interface_name][attr[0]] = attr[1]
    print(f"\n\n||||||||| Interface {interface_name} ||||||||||||||")
out = pp.pformat(links)
out = out.replace(",", ",\n")
out = out.replace(",\n\n", ",\n")
print(out)

# Go get addresses
# from the .__doc__
"""
Dump addresses.

If family is not specified, both AF_INET and AF_INET6 addresses will be dumped::

# get all addresses
ip.get_addr()

It is possible to apply filters on the results::

# get addresses for the 2nd interface
ip.get_addr(index=2)

# get addresses with IFA_LABEL == 'eth0'
ip.get_addr(label='eth0')

# get all the subnet addresses on the interface, identified
# by broadcast address (should be explicitly specified upon
# creation)
ip.get_addr(index=2, broadcast='192.168.1.255')

A custom predicate can be used as a filter::

ip.get_addr(match=lambda x: x['index'] == 1)
"""
for link in link_table:
    a4 = ip.get_addr(family=AF_INET, label=link)
    a6 = ip.get_addr(family=AF_INET6, label=link)
    addr_table[link][AF_INET] = convert(a4)
    addr_table[link][AF_INET6] = convert(a6)
pp.pprint(addr_table)

ipv4_addrs = ip.get_addr(family=AF_INET)
print("++++++++ IPv4 addresses +++++++")
pp.pprint(ipv4_addrs)

ipv4_addrs = ip.get_addr(family=AF_INET6)
print("66666 6666666  IPv6 addresses 66666666 ")
pp.pprint(ipv4_addrs)
