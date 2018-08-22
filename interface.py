#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Dealing with interfaces

import os
from typing import Dict, List

import constants
from layer import Layer
from utilities import OsCliInter


class Interface(Layer):
    """
    Methods for dealing with interfaces.  An "interface" for the purposes of this program
    is a combination of the physical and data link layers in the OSI model, and the
    network access layer in the TCP/IP model
    """

    def __init__(self, if_name: str) -> None:
        """
        Both DataLink and PhysicalLinks have interface names

        """
        super().__init__()
        assert hasattr(self, 'time'), "During the instantiation of an " \
                                      "Interface object, the time attribute " \
                                      "was not added by the Layer superclass"
        # Be consistent in the convention of naming interfaces
        self.if_name = if_name if ":" in if_name else if_name + ":"

    @staticmethod  # Leave as a static method as there are discover
    # methods in subclasses
    def discover() -> Dict[str, "Interface"]:  # Interface
        """
        Find all of the interfaces in a system
        :return: A dictionary of interfaces in a system.
        """
        raise NotImplementedError

    @staticmethod
    def set_discover_ip_command() -> str:
        # The location of the command to get the interface information is OS specific and common
        # across all interfaces, so it is a class variable
        if 'Linux' == OsCliInter.system:
            # The command to get network access information from the OS.  I suppose it could be in /sbin or /usr/sbin
            if os.path.isfile("/bin/ip"):
                ip_command: str = "/bin/ip"
            elif os.path.isfile("/usr/bin/ip"):
                ip_command: str = "/usr/bin/ip"
            else:
                raise FileNotFoundError("Could not find the ip command, not in /bin/ip nor in /usr/bin/ip")
        else:
            raise NotImplementedError(f"System {OsCliInter.system} not implemented yet")
        return ip_command

    @staticmethod
    def set_discover_layer_command(layer) -> List[str]:
        """

        :rtype: List    A list of strings that is the command to pass to subprocess.run_command
        """
        # the ip link list or ip addr list commands instead of the ip link show DEV command
        # For a complete list of flags and parameters, see
        # http://man7.org/linux/man-pages/man7/netdevice.7.html
        if "link" != layer and "addr" != layer:
            raise ValueError(f"layer is '{layer}' and should be either 'link' or 'addr' ")
        if 'Linux' == OsCliInter.system:
            discover_command = [Interface.IP_COMMAND, "--oneline", layer, "list"]
        elif 'Windows' == OsCliInter.system:
            raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
        elif 'Mac OS' == OsCliInter.system:
            raise NotImplementedError(f"System is {OsCliInter.system} and I haven't written it yet")
        else:
            raise ValueError(f"System is {OsCliInter.system} and I don't recognize it")
        return discover_command


# end of class Interface **********
Interface.IP_COMMAND: str = Interface.set_discover_ip_command()


class PhysicalLink(Interface):
    """
    Methods for dealing with links.  A link is, for example, a wifi transceiver, an ethernet network interface
    card (NIC)
    For purposes of this program, a link is the information returned by the "ip --online link show" command
    """

    # A dictionary of Physical Links, key'd by interface name.  The values are PhysicalLink objects
    physical_link_dict: Dict[str, "PhysicalLink"] = dict()

    def __init__(self, if_name, state_up, broadcast, multicast, lower_up, carrier,
                 mtu, qdisc, state, mode, group, qlen, link_addr, broadcast_addr, **kwargs) -> None:
        super().__init__(if_name)
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

    # Get a dictionary of all PhysicalLinks.  Note that there is a many-to-many
    # relationshp between DataLinks and PhysicalLinks because a PhysicalLink
    # might have several IPv4 or IPv6 addresses, and a DataLink might span
    # several PhysicalLinks (in the case of bonded interfaces using
    # LACP (Link Aggration Control Protocol)
    @staticmethod  # keep discover as a static method inside
    # class PhysicalLink because there is a method
    # discover in class DataLink
    def discover() -> None:  # PhysicalLink
        """
        Discover all of the physical links on this system
        :rtype: A dictionary of physical keyed by interface name
        :return:
        """
        global physical_link_dict
        if "Linux" != OsCliInter.system:
            raise NotImplementedError(f"In PhysicalLink.discover, {OsCliInter.system} is not implemented")
        else:
            assert "link" in PhysicalLink.DISCOVER_LINK_COMMAND, \
                "In PhysicalLink.discover, the word 'link' is not in the " \
                "DISCOVER_COMMAND"
        lnk_str: str = OsCliInter.run_command(PhysicalLink.DISCOVER_LINK_COMMAND)
        interface_list_strs: List[str] = lnk_str.split("\n")
        for if_str in interface_list_strs:
            fields = if_str.split()
            if len(fields) <= 1:  # skip blank lines
                continue
            # fields[0] is the line number, skip that.  fields[1] is the device name.  trailing colon
            if_name = fields[1]
            assert ":" in if_name, f": not found in data physical name {if_name} and it should be there"
            assert if_name not in PhysicalLink.physical_link_dict, \
                f"{if_name} is *already* in PhysicalLink.physical_link_dict and should not be"
            physical_link_obj = physical_link_from_if_str(if_str=if_str)
            PhysicalLink.physical_link_dict[if_name] = physical_link_obj


# END OF CLASS PhysicalLink
# Make DISCOVER_LINK_COMMAND a class (not an object) attribute
PhysicalLink.DISCOVER_LINK_COMMAND: List = Interface.set_discover_layer_command("link")


def physical_link_from_if_str(if_str, **kwargs):
    """
    :param  if_str  a string (which is OS dependent), which describes the physical link
    """

    if "Linux" == OsCliInter.system:
        # Assumes if_str is the result of the ip --oneline link show DEV command
        fields = if_str.split()
        if_name = fields[1]
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
    link_obj = PhysicalLink(if_name=if_name,
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


class DataLink(Interface):
    """
    Methods for the data link layer in the OSI model: IP addresses
    """

    # a dictionary of Interface objects, keyed by interface name.   The values are DataLink objects
    data_link_dict: Dict[str, List["DataLink"]] = dict()

    # DataLink constructor
    def __init__(self, if_name: str, addr, mask, brd, scope, dynamic, noprefixroute, valid_lft, preferred_lft) -> None:
        """

        :rtype: None
        """
        super().__init__(if_name=if_name)
        # In a future version, I will do a better job of separating IPv4 and IPv6 addresses
        self.address = addr
        self.brd = brd  # May be None if address is an IPv6 address
        self.mask = mask
        assert scope == "global" or scope == "link" or scope == "host", f"scope should be either 'global' or " \
                                                                        f"'link' or 'host', not {scope}"
        self.scope = scope
        self.dynamic = dynamic
        self.noprefixroute = noprefixroute
        self.valid_lft = valid_lft
        self.preferred_lft = preferred_lft

    # discover all of the data links on the current system
    # The correspondence of data links and phyicals links will NOT be one to one, because some physical links will
    # not have any IP addresses, and some IP addresses will be bound across multiple interfaces
    @staticmethod    # Do not convert to a static function because there are 2 other discover functions
    def discover():  # DataLink
        """
        Call this method to discover all of the data links in the system.
        :return:   A class dictionary of lists of data links.  A single physical link may have several data links

        """
        global data_link_dict
        if "Linux" != OsCliInter.system:
            raise NotImplementedError(f"In DataLink.discover, {OsCliInter.system} is not implemented")
        lnk_str: str = OsCliInter.run_command(DataLink.DISCOVER_ADDR_COMMAND)
        interface_list_strs: List[str] = lnk_str.split("\n")
        for if_str in interface_list_strs:
            fields = if_str.split()
            if len(fields) <= 1:  # skip blank lines
                continue
            # fields[0] is the line number, skip that.  fields[1] is the
            # device name.  No trailing colonm from the command, so add one
            if_name = fields[1] + ":"
            data_link_obj: DataLink = data_link_from_if_str(fields=fields)
            if if_name in DataLink.data_link_dict:
                DataLink.data_link_dict[if_name].append(data_link_obj)
            else:
                DataLink.data_link_dict[if_name] = [data_link_obj]


# end of class DataLink  ##########

DataLink.DISCOVER_ADDR_COMMAND: List = DataLink.set_discover_layer_command("addr")


def data_link_from_if_str(fields: List[str]) -> 'DataLink':
    """
    :rtype: Datalink
    :param fields: List of strs which is the output of ip command (linux)
    :return: DataLink   an object which corresponds
    """
    assert "mtu" not in fields,\
        "Passed the results of the ip link command instead of ip addr command"
    assert "Linux" == OsCliInter.system
    #
    if_name = fields[1]
    assert "/" in fields[3], f"'/' not in fields[3], which is {fields[3]} ."
    address_, mask = fields[3].split("/")
    if fields[2] == "inet":
        #            ipv6_address = None
        assert fields[4] == "brd", "fields[4] should be 'brd' (Because this "\
                                 f"is an IPv4 address) but is actually " + fields[4]
        brd = fields[5]
        fc = 6  # Field counter
    elif fields[2] == "inet6":
        #           ipv4_address = None
        brd = None
        fc = 4  # Field counter
    else:
        raise AssertionError("fields[2] is neither 'inet' nor 'inet6' ")
    """
    jeffs@jeffs-desktop:/home/jeffs  $ ip --oneline addr show dev eno1
3: eno1    inet 192.168.0.3/24 brd 192.168.0.255 scope global dynamic noprefixroute eno1\       valid_lft 60292sec 
preferred_lft 60292sec
3: eno1    inet6 2602:4b:ac60:9b00:ae37:ff43:3d79:3daf/64 scope global noprefixroute \       valid_lft forever 
preferred_lft forever
3: eno1    inet6 fd00::ae7f:4068:cb55:3152/64 scope global noprefixroute \       valid_lft forever preferred_lft 
forever
3: eno1    inet6 fe80::59d:1419:ef30:64de/64 scope link noprefixroute \       valid_lft forever preferred_lft 
forever
jeffs@jeffs-desktop:/home/jeffs  $ 

    """

    assert fields[fc] == "scope", f"There is an error in field_ctr. field[{fc}] \ " \
                                  f"should be 'scope' but is really {fields[fc]}. "
    fc += 1
    scope = fields[fc]
    # Scope is checked in DataLink.__init__
    fc += 1
    # Next are a bunch of keywords that are either present or absent
    # See https://www.systutorials.com/docs/linux/man/8-ip-address/ for details
    dynamic = "dynamic" in fields[fc:]
    noprefixroute = "noprefixroute" in fields[fc:]
    # valid_lft LFT
    # the valid lifetime of this address; see section 5.5.4 of RFC 4862. When it expires, the address is removed by
    # the kernel. Defaults to forever.
    # preferred_lft LFT
    # the preferred lifetime of this address; see section 5.5.4 of RFC 4862. When it expires, the address is no
    # longer used for new outgoing connections. Defaults to forever.
    #
    # I have seen the value 60292sec on several interfaces.  That's a little more than 16 hours, 45 minutes.
    """
    if fields[fc] == "forever":
        valid_lft = constants.MAXINT    # 2^32 seconds = ~ 136 years
    else:
        assert fields[fc][-3:] == "sec", f"fields[{fc}][:-3]n shouldn be 'sec' but is actually {fields[fc][:-3]} "
        valid_lft = int(fields[fc][-3:])
    """
    data_link_obj: DataLink = DataLink(if_name=if_name, addr=address_,
                                       brd=brd, mask=mask, scope=scope, dynamic=dynamic,
                                       noprefixroute=noprefixroute,
                                       valid_lft=constants.MAXINT, preferred_lft=constants.MAXINT)
    return data_link_obj


if __name__ == "__main__":

    PhysicalLink.discover()
    DataLink.discover()

    print("Physical links ", '*' * 40)
    for physical_link in PhysicalLink.physical_link_dict:
        assert isinstance(physical_link, PhysicalLink)
        mac_addr = physical_link.link_addr
        if_name3 = physical_link.if_name
        print(if_name3, mac_addr, physical_link.state)

    print("Data links ", '*' * 40)
    for data_link in DataLink.data_link_dict:
        assert isinstance(data_link, DataLink)
        address = data_link.address
        if_name3 = data_link.if_name
        print(if_name3, address, data_link.mask)
