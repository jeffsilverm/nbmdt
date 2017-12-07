#! /usr/bin/env python3
# _*_ coding: utf-8 _*_
#
# networks.py
# This file has class Networks which stores a list of remote hosts that should be tested

#
class Networks(object):
    def __init__(self):
        self.remote_hosts = ["google.com", "f5.com", "commercialventvac.com"]

    @staticmethod
    def find_networks():
        pass


