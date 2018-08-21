#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Dealing with interfaces

import os
import typing
import sys

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

    @classmethod
    def discover(cls) -> typing.Dict[str, "Interface"]:
        """
        Find all of the interfaces in a system
        :return: A dictionary of interfaces in a system.
        """
        raise NotImplementedError

    @classmethod
    def set_discover_command(cls, layer):
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
            discover_command = [IP_COMMAND, "--oneline", layer, "list"]
        elif 'Windows' == OsCliInter.system:
            discover_command = None
            raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
        elif 'Mac OS' == OsCliInter.system:
            discover_command = None
            raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
        else:
            discover_command = None
            raise ValueError(f"System is {OsCliInter.system} and I don't recognize it")
        return discover_command




class PhysicalLink(Interface):
    """
    Methods for dealing with links.  A link is, for example, a wifi transceiver, an ethernet network interface
    card (NIC)
    For purposes of this program, a link is the information returned by the "ip --online link show" command
    """

    DISCOVER_COMMAND = Interface.set_discover_command("link")

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
        DISCOVER_COMMAND = [IP_COMMAND, "--oneline", "link", "list"]
    elif 'Windows' == OsCliInter.system:
        DISCOVER_COMMAND = None
        raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
    elif 'Mac OS' == OsCliInter.system:
        DISCOVER_COMMAND = None
        raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
    else:
        DISCOVER_COMMAND = None
        raise ValueError(f"System is {OsCliInter.system} and I don't recognize it")

    # A dictionary of Physical Links, key'd by interface name.  The values are PhysicalLink objects
    physical_link_dict:typing.Dict[str,"PhysicalLink"] = dict()

    def __init__(self, if_name, state_up, broadcast, multicast, lower_up, carrier,
                 mtu, qdisc, state, mode, group, qlen, link_addr, broadcast_addr, **kwargs):
        Inteface.__init__()
        self.if_name = if_name

        assert type(state_up) == bool, f"state_up is {type(state_up)}"
        self.broadcast = broadcast
        self.multicast = multicast
        self.state_up = state_up
        self.lower_up = lower_up
        self.carrier = carrier
        self.mtu = mtu
        self.qdisc = qdisc
        self.state = state
        self.mode = mode
        self.group = group
        self.qlen = qlen
        self.link_addr = link_addr
        self.broadcast_addr = broadcast_addr
        for k in kwargs:
            self.__setattr__(k, kwargs[k])


    @staticmethod
    def physical_link_from_if_str(self, if_str, **kwargs):
        """
        :param  if_str  a string (which is OS dependent), which describes the physical link
        """

        if "Linux" == OsCliInter.system:
            # Assumes if_str is the result of the ip --oneline link show DEV command
            fields = if_str.split()
            if_name = fields[1][:-1]  # the ip commnand has a trailing colon on links, but not on addresses
            flags = fields[2]
            broadcast = "BROADCAST" in flags
            multicast = "MULTICAST" in flags
            state_up = "UP" in flags
            lower_up = "LOWER_UP" in flags
            carrier = "NO-CARRIER" not in flags

            mtu = fields[4]
            qdisc = fields[6]
            state = fields[8]
            mode = fields[10],
            group = fields[12],
            qlen = fields[14],
            link_addr = fields[16]
            broadcast_addr = fields[18]
        else:
            raise NotImplementedError(f"{OsCliInter.system} is not implemented yet in PhysicalLink")
        link_obj = self.__init__(if_name=if_name,
                                 state_up=state_up,
                                 broadcast=broadcast,
                                 multicast=multicast,
                                 lower_up=lower_up,
                                 carrier=carrier,
                                 mtu=mtu,
                                 qdisc=qdisc,
                                 state=state,
                                 mode=mode,
                                 group=group,
                                 qlen=qlen,
                                 link_addr=link_addr,
                                 broadcast_addr=broadcast_addr,
                                 kwargs=kwargs)
        return link_obj

    @classmethod
    def discover(cls) -> None:
        """
        Discover all of the physical links on this system
        :return:
        """

class DataLink(Interface):
    """
    Methods for the data link layer in the OSI model: IP addresses
    """
    DISCOVER_COMMAND = Interface.set_discover_command("addr")

    # a dictionary of Interface objects, keyed by interface name.   The values are DataLink objects
    data_link_dict:typing.Dict[str,"DataLink"]  = dict()

    # DataLink constructor
    def __init__(self, if_name, address, mask, brd, scope, prefixroute, valid_lft, preferred_lft):
        self.if_name = if_name
        # In a future version, I will do a better job of separating IPv4 and IPv6 addresses
        self.address = address
        self.brd = brd  # May be None if address is an IPv6 address
        self.mask = mask
        assert scope == "global" or scope == "link" or scope == "host", f"scope should be either 'global' or " \
                                                                        f"'link' or 'host', not {scope}"
        self.scope = scope
        self.prefixroute = prefixroute
        self.valid_lft = valid_lft
        self.preferred_lft = preferred_lft

    # discover all of the data links on the current system
    # The correspondence of data links and phyicals links will NOT be one to one, because some physical links will
    # not have any IP addresses, and some IP addresses will be bound across multiple interfaces
    @classmethod
    def discover(cls):
        """
        Call this method to discover all of the interfaces in the system.  This command
        will call the command line command to list all of the interfaces
        :return:
        """

        if "Linux" != OsCliInter.system:
            raise NotImplementedError(f"In DataLink.discover, {OsCliInter.system} is not implemented")
        lnk_str: str = OsCliInter.run_command(cls.DISCOVER_COMMAND)
        interface_list_strs: typing.List[str] = lnk_str.split()
        for if_str in interface_list_strs:
            fields = if_str.split()
            if len(fields) <= 1:         # skip blank lines
                continue
            # fields[0] is the line number, skip that.  fields[1] is the device name.  No trailing colon
            if_name = fields[1]
            assert ":" not in if_name, f": found in data link name {if_name} and it shouldn't be there"
            cls.data_link_dict[if_name] = cls.data_link_from_if_str(fields=fields)

    @staticmethod
    def data_link_from_if_str(cls, fields):
        assert "Linux" == OsCliInter.system
        if_name = fields[1]
        address, mask = fields[3].split("/")
        if fields[2] == "inet":
            address = address
            ipv6_address = None
            brd = fields[5]
        elif fields[2] == "inet6":
            address = address
            ipv4_address = None
            brd = None
        else:
            raise AssertionError("fields[2] is neither 'inet' nor 'inet6' ")

        data_link_obj = cls.__init__(if_name=if_name, address=address, brd=brd, mask=mask)

        return data_link_obj


if __name__ == "__main__":

    Interface.PhysicalLink.discover()
    Interface.DataLink.discover()

    print("Physical links ", '*' * 40)
    for physical_link in Interface.PhysicalLink.physical_link_dict:
        assert isinstance(physical_link, Interface.PhysicalLink)
        mac_addr = physical_link.link_addr
        if_name = physical_link.if_name
        print(if_name, mac_addr, physical_link.state)

    print("Data links ", '*' * 40)
    for data_link in Interface.DataLink.data_link_dict:
        assert isinstance(data_link, Interface.DataLink )
        address = data_link.address
        if_name = data_link.if_name
        print(if_name, address, data_link.mask)
