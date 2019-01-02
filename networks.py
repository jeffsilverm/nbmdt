#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#
# This file contains information on networks

# From https://pypi.org/project/pyroute2/
# pyroute2 uses netlink which is a socket based interface to the kernel.
# See also RFC 3549 "Linux Netlink as an IP Services Protocol"
# https://tools.ietf.org/html/rfc3549
#
from socket import AF_INET
#from pyroute2 import IPRoute

# get access to the netlink socket
#ip = IPRoute()

# Maybe pyroute2 is too complicated for what I want to do, I just want
# read the IPv4 and IPv6 routing tables.
# Look at notes_2018-12.html#mozTocId983008

class Networks(object):
    def __init__(self):
        self.remote_hosts = []

    @staticmethod
    def find_networks():
        pass


