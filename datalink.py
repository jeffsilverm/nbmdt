#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# Dealing with the DataLink layer in the OSI model 
# Media Access Control (Ethernet addresses)
#
#

import enum
import sys
from typing import Dict, List

import constants
from interfaces import PhysicalInterface
from utilities import OsCliInter, os_name, the_os


class DataLink(PhysicalInterface):
    # Create a command, suitable for executing by subprocess, that lists all of the datalinks on this system.
    if constants.OperatingSystems.LINUX == the_os:
        DISCOVER_ALL_DATALINKS_COMMAND = [PhysicalInterface.IP_COMMAND, "--oneline", "link", "list"]
    else:
        raise NotImplemented(
            f"The DISCOVER_ALL_DATALINKS_COMMAND can't be filled in yet because {os_name} isn't implemented yet")

    class ProtocolName(enum.IntEnum):
        # From https://www.iana.org/assignments/ieee-802-numbers/ieee-802-numbers.xhtml
        # These constants are here because these numbers exist only in Ethernet and other IEEE-802 LAN frame headers
        IPv6 = 0x86DD  # RFC 7042
        IPv4 = 0x0800  # RFC 7042

    datalinks_dict: Dict[str, "DataLink"] = dict()

    def __init__(self, name, state_up, broadcast, multicast, lower_up, carrier,
                 mtu, qdisc, state, mode, group, qlen, link_addr, broadcast_addr, **kwargs) -> None:
        # Be consistent in the convention of naming interfaces
        name = name if ":" in name else name + ":"
        super().__init__(name=name)

        assert type(broadcast) == bool, f"broadcast_up is {type(broadcast)}, should be bool"
        self.broadcast = broadcast
        assert type(multicast) == bool, f"multicast_up is {type(multicast)}, should be bool"
        self.multicast = multicast
        assert type(state_up) == bool, f"state_up is {type(state_up)}, should be bool"
        self.state_up = state_up
        assert type(lower_up) == bool, f"lower_up is {type(lower_up)}, should be bool"
        self.lower_up = lower_up
        assert type(carrier) == bool, f"carrier is {type(carrier)}, should be bool"
        self.carrier = carrier
        assert type(mtu) == int, f"MTU is {type(mtu)}, should be int"
        self.mtu = mtu
        self.qdisc = qdisc
        self.state = state
        self.mode = mode
        self.group = group
        assert type(qlen) == int or qlen is None, f"qlen is type {type(qlen)} should be either int or None"
        self.qlen = qlen
        self.link_addr = link_addr  # Maybe mac_addr or eth_addr would be a better name
        self.broadcast_addr = broadcast_addr

        # Here is a place for counters
        for k in kwargs:
            self.__setattr__(k, kwargs[k])

    # Get a dictionary of all datalinks.  Note that there is a many-to-many
    # relationshp between a MAC and an IP address: a NIC (with a single MAC)
    # might have several IPv4 or IPv6 addresses, and an IP address might span
    # several MACs (in the case of bonded interfaces using
    # LACP (Link Aggration Control Protocol)
    @classmethod
    def discover(cls):  # DataLink
        """
        Discover all of the physical links on this system
        :rtype: A dictionary of DataLinks  keyed by interface name
        :return:
        """

        if the_os != constants.OperatingSystems.LINUX:
            raise NotImplementedError(f"In DataLink.discover, {os_name} is not implemented")
        else:
            assert "link" in cls.DISCOVER_ALL_DATALINKS_COMMAND, \
                f"In DataLink.discover, the word 'link' is not in the DISCOVER_COMMAND {cls.DISCOVER_ALL_DATALINKS_COMMAND}"
            assert "--oneline" in cls.DISCOVER_ALL_DATALINKS_COMMAND, \
                f"In DataLink.discover, the option --oneline is not in the DISCOVER_COMMAND " \
                f"{cls.DISCOVER_ALL_DATALINKS_COMMAND}"
            datalinks_str: str = OsCliInter.run_command(cls.DISCOVER_ALL_DATALINKS_COMMAND)
            # The rest of this stanza is decoding the output of the ip command
            datalinks_list_strs: List[str] = datalinks_str.split("\n")
            for if_str in datalinks_list_strs:
                fields = if_str.split()
                if len(fields) <= 1:  # skip blank lines
                    continue
                # fields[0] is the line number, skip that.  fields[1] is the device name.  trailing colon
                name: str = fields[1]
                assert ":" in name, f": not found in interface name {name} and it should be there"
                # If I am discovering something and what I discover is already known, then I'm not really discovering
                # anything, am I?  On the other hand, what if I call discover more than once?
                if name in cls.datalinks_dict:
                    print(f"{name} is *already* in DataLink.datalinks_dict and should not be, I think",
                          file=sys.stderr)
                datalink_obj = cls.datalink_from_if_str(if_str=if_str)
                DataLink.datalinks_dict[name] = datalink_obj

    def set_name(self, name: str) -> None:
        """
        This is the germ of a setter that can be used to add information to an interface
        It isn't clear to me if a method in DataLink should a method in Ip or vice-versa
        Also, consider the use case of a virtual interface, such as eno1:1
        Test this with
        jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development) *  $ sudo ifconfig eno1:1
        eno1:1: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.3.47  netmask 255.255.255.0  broadcast 192.168.3.255
        ether 00:22:4d:7c:4d:d9  txqueuelen 1000  (Ethernet)
        device interrupt 20  memory 0xf7900000-f7920000
        # Issue 21
        # https://github.com/jeffsilverm/nbmdt/issues/21

jeffs@jeffs-desktop:/home/jeffs/python/nbmdt  (development)

        :param name:   The name of the interface
        :return:
        """
        assert isinstance(name, str), f"name is of type {type(name)}, should be str"
        self.name = name

    @staticmethod
    def datalink_from_if_str(if_str, **kwargs):
        """
        This method accepts a string, presumably from the ip command (linux), the TBD command
        (windows) or the TBD command (Mac OS X).  It then creates a DataLink object
        :param  if_str  a string (which is OS dependent), which describes the interface at the media access control or
        datalink level
        """

        if constants.OperatingSystems.LINUX == the_os:
            # Assumes if_str is the result of the ip --oneline link show DEV command
            fields = if_str.split()
            name: str = fields[1]
            flags: str = fields[2]
            broadcast: bool = "BROADCAST" in flags
            multicast: bool = "MULTICAST" in flags
            state_up: bool = "UP" in flags
            lower_up: bool = "LOWER_UP" in flags
            carrier: bool = "NO-CARRIER" not in flags

            mtu: int = int(PhysicalInterface.get_value_from_list(fields, "mtu"))
            qdisc: str = PhysicalInterface.get_value_from_list(fields, "qdisc")
            state: str = PhysicalInterface.get_value_from_list(fields, "state")
            mode: str = PhysicalInterface.get_value_from_list(fields, "mode")
            group: str = PhysicalInterface.get_value_from_list(fields, "group")
            qlen_str: str = PhysicalInterface.get_value_from_list(fields, "qlen")  # The qlen_str may have a trailing \
            if qlen_str[-1:] == """\\""":
                qlen_str = qlen_str[:-1]
            try:
                qlen: int = int(qlen_str)
            except ValueError:
                print("qlen_str is not a valid int.  It's " + qlen_str, file=sys.stderr)
                print(f"if_str is {if_str}\n", file=sys.stderr)
                qlen = 0  # moving on
            if name == "lo:":
                link_addr: str = PhysicalInterface.get_value_from_list(fields, "link/loopback")
            else:
                link_addr: str = PhysicalInterface.get_value_from_list(fields, "link/ether")
            assert len(link_addr) > 0, "link_addr has length 0.  " \
                                       f"get_value_from_list failed. fields is {fields}"
            broadcast_addr: str = PhysicalInterface.get_value_from_list(fields, "brd")
        else:
            raise NotImplemented(f"{OsCliInter.system} is not implemented yet in DataLink")
        link_obj = DataLink(name=name,
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

    # END OF CLASS DataLink

if __name__ == "__main__":
    DataLink.discover()

    print("NICS with datalinks ", '*' * 40)
    for datalink in DataLink.datalinks_dict.values():
        assert isinstance(datalink, DataLink), \
            f"datalink should be an instance of DataLink, but it's actually {type(datalink)}."
        mac_addr = datalink.link_addr
        name = datalink.name
        print(name, mac_addr, datalink.state, "broadcast is "+str(datalink.broadcast), f"carrier is {str(datalink.carrier)}", f"MTU is {datalink.mtu} bytes")
