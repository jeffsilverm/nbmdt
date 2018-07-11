#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import subprocess
from platform import system
from typing import Union

import collections

from constants import ErrorLevels
# from entities import Entity
from utilities import OsCliInter


# There is an ip command cheat sheet at
# https://access.redhat.com/sites/default/files/attachments/rh_ip_command_cheatsheet_1214_jcs_print.pdf

def none_if_none(s):
    return s if s is not None else "None"


# Originally, I was going to have an Entity class which would have some information common to interfaces,
# MAC addresses, IPv4 and IPv6 routes, transports, sessions, presentations, and applications, but I just couldn't
# get my head around it, which suggests to me that maybe it wasn't such a good idea.
class Interface(object):
    my_os = system()
    if my_os == 'Linux':
        # This should be a configuration file item - on ubuntu, the IP_COMMAND is /bin/ip .  So what I did was
        # symlink it so that both /bin/ip and
        # /usr/sbin/ip work.  But I can do that because I am a sysadmin.
        # Issue 2 https://github.com/jeffsilverm/nbmdt/issues/2
        if os.path.isfile("/bin/ip"):
            IP_COMMAND = "/bin/ip"
        elif os.path.isfile("/usr/bin/ip"):
            IP_COMMAND = "/usr/bin/ip"
        else:
            raise FileNotFoundError("Could not find the ip command, not in /bin/ip nor in /usr/bin/ip")
        discover_command = [IP_COMMAND, "--details", "--oneline", "link", "list"]
        get_details_command = [IP_COMMAND, "--details", "--oneline", "link", "show"]
        get_stats_command = [IP_COMMAND, "--stats", "--oneline", "link", "show"]
    elif my_os == 'Windows':
        raise NotImplementedError(f"System is {my_os} and I haven't written it yet")
    elif my_os == 'Mac OS':
        raise NotImplementedError(f"System is {my_os} and I haven't written it yet")
    else:
        raise ValueError(f"System is {my_os} and I don't recognize it")

    def __init__(self, name: str, lnk_str: str = None) -> None:
        """
        Creates an Interface object which is a child object of Layer
        :param name: The name of the interface
        :param lnk_str: The string from the command that was used to figure out this interface
        """
        self._name = name
        self._timestamp = datetime.datetime.now()
        # Did the caller specify a string with the description of the interface?  That might be if the caller called
        # the ip link list command instead of the ip link show DEV command
        # For a complete list of flags and parameters, see
        # http://man7.org/linux/man-pages/man7/netdevice.7.html

        if lnk_str is None:
            command: list = self.get_details_command.append(name)
            lnk_str: str = OsCliInter.run_command(command)
        if self.my_os != 'Linux':  # os.uname().sysname
            raise NotImplementedError(f"os.uname().sysname returned {self.my_os}."
                                      "This version is only implemented for linux")
        fields = lnk_str.split()
        # fields[0] is the line number, skip that.  fields[1] is the device name
        # See Issue 17, https://github.com/jeffsilverm/nbmdt/issues/17
        if fields[1][:-1] == ":":
            self.name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
        else:
            self.name = fields[1]
        flags = fields[2]
        self.state_up = "UP" in flags
        self.broadcast = "BROADCAST" in flags
        self.lower_up = "LOWER_UP" in flags
        self.carrier = "NO-CARRIER" not in flags
        self.multicase = "MULTICAST" in flags

        for idx in range(3, len(fields) - 1, 2):
            # Accortding to http://lartc.org/howto/lartc.iproute2.explore.html , qdisc stands for "Queueing
            # Discipline" and it's vital.
            if fields[idx] == "mtu":
                self.mtu = fields[idx + 1]
                # Issue 16, https://github.com/jeffsilverm/nbmdt/issues/16f
            elif fields[idx] == "link/ether" or fields[idx] == "link/ether" :
                self.ether = fields[idx + 1]
            elif fields[idx] == "brd":
                self.brd = fields[idx + 1]
            else:
                self.__setattr__(fields[idx], fields[idx + 1])

    def get_status(self) -> ErrorLevels:
        """Return the status of this interface.
        CAUTION: this is a cache and there is always the problem of maintaining cache coherentcy"""
        raise NotImplementedError

    @classmethod
    def discover(cls):
        """
        Discover all of the interfaces on this machine

        :return:    a dictionary of interfaces, key'd by name.  The value is an Interface object
        """

        completed_str = OsCliInter.run_command(cls.discover_command).rstrip()
        links_list = completed_str.split('\n')
        assert len(links_list) > 0, f"The length of the links_list is 0, output of discover_command is {completed_str}"
        link_dict = dict()
        for lnk in links_list:
            fields = lnk.split()
            # fields[0] is the line number, skip that.  fields[1] is the device name
            intf_name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
            link_dict[intf_name] = Interface(intf_name, lnk)

        return link_dict

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def set_stats(self):
        """This method sets the statistics for the interface"""





if __name__ == "__main__":
    # nominal = SystemDescription.describe_current_state()

    # Create a dictionary, keyed by link name, of the physical interfaces
    link_db = Interface.discover()
    # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
    # addr_db = LogicalInterface.get_all_logical_interfaces()

    print("links ", '*' * 40)
    for link in link_db.keys():
        link_int_descr = link_db[link]
        mac_addr = link_int_descr.m if 'link/ether' in \
                                                   link_int_descr else "00:00:00:00:00:00"
        print(link, mac_addr, link_int_descr['state'])

    """
    print("Addresses ", '*' * 40)
    for addr_name in addr_db:
        print("\n{}\n".format(addr_name))
        for addr in addr_db[addr_name]:  # The values of the addr_db are descriptions of addresses
            assert isinstance(addr, LogicalInterface)
            print("   " + str(addr))
    """
