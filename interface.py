#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Dealing with interfaces

import os
import sys
from typing import Dict, List

import constants
from layer import Layer
from utilities import OsCliInter, os_name, the_os





class Interface(Layer):
    """
    Methods for dealing with interfaces.  An "interface" for the purposes of this program
    is a combination of the physical and data link layers in the OSI model, and the
    network access layer in the TCP/IP model
    """

    def __init__(self, name: str) -> None:
        """
        Both Macs and IP endpoints have names, and whenever an Interface object is created,
        record the time it was created at.

        In the future, I might want to create some sort of statistics object that has
        the time stamp and the counters.

        """
        # Be consistent in the convention of naming interfaces
        self.name = name if ":" in name else name + ":"
        super().__init__(name=name)
        assert hasattr(self, 'time'), "During the instantiation of an " \
                                      "Interface object, the time attribute " \
                                      "was not added by the Layer superclass"

    # This is linux specific
    def get_value_from_list(self: list, keyword: str) -> str:
        """
        The output of the ip command commonly has a keyword which is either
        present or not, and if it is present, might be followed by a value,
        depending on what the keyword is.  The output is in a list of strings.
        This method returns an empty string if the keyword does not appear in the
        list of strings, and returns the value if the keyword does appear in the
        list of strings
        :rtype: str
        """

        if keyword in self:
            idx = self.index(keyword)
            value = self[idx + 1]
            return value
        else:
            return ""



    @staticmethod  # Leave as a static method as there are discover
    # methods in subclasses
    def discover() -> Dict[str, "Interface"]:  # Interface
        """
        Find all of the interfaces in a system
        :return: A dictionary of interfaces in a system.
        """
        raise NotImplementedError


    # The ip command shows up either in /bin/ip or in /usr/bin/ip.  This is very linux specific
    IP_COMMAND = None
    # The location of the command to get the interface information is OS specific and common
    # across all interfaces, so it is a class variable
    # Insofar as I know, this is linux specific.
    if the_os == constants.OperatingSystems.LINUX:
        # The command to get network access information from the OS.  I suppose it could be in /sbin or /usr/sbin
        if os.path.isfile("/bin/ip"):
            IP_COMMAND: str = "/bin/ip"
        elif os.path.isfile("/usr/bin/ip"):
            IP_COMMAND: str = "/usr/bin/ip"
        else:
            raise FileNotFoundError(
                f"Could not find the ip command, not in /bin/ip nor in /usr/bin/ip os is {os_name}")
    else:
        raise NotImplementedError(f"System {os_name} not implemented yet")



    # This is poorly named
    # Issue 22
    # https: // github.com / jeffsilverm / nbmdt / issues / 22
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
        if the_os == constants.OperatingSystems.LINUX:
            discover_command = [Interface.IP_COMMAND, "--oneline", layer, "list"]
        elif the_os == constants.OperatingSystems.WINDOWS:
            raise NotImplementedError("System is windows and I haven't written it yet")
        elif the_os == constants.OperatingSystems.MAC_OS_X:
            raise NotImplementedError("System is Mac OS X and I haven't written it yet")
        elif the_os == constants.OperatingSystems.BSD:
            raise NotImplementedError("System is BSD and I haven't written it yet")
        elif the_os == constants.OperatingSystems.UNKNOWN:
            raise ValueError(f"System is {os_name} and it's unknown to this program")
        else:
            raise AssertionError(f"System is {os_name} which is a bad value")

        return discover_command


# end of class Interface **********
# The rest of what was in interface.py is now in guts_of_interface.py for eventual removal




if __name__ == "__main__":
    if the_os == constants.OperatingSystems.LINUX:
        print(f"Using linux, the ip command is at {Interface.IP_COMMAND}")
        results = OsCliInter.run_command([Interface.IP_COMMAND, "link", "list"])
        print(f"The results of running the 'ip link list' command are\n{results}")