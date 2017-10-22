#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
"""
configuration.py is responsible for handling all configuration chores for the NBMDT.  There are two configurations: a
fixed configuration set by the system administrator only and a read-write configuration which is initially set by the
system administrator and then changed as needed by the program

"""
import configparser
import sys
import os


class FixedConfiguration(object):
    """
    An object of FixedConfiguration has the read-only configuration for nbmdt
    """

    def __init__(self, ini_filename: str):
        """
        This method creates a FixedConfiguration object from the file ini_filename
        :param ini_filename:  str
        """

        self.__ini_filename = ini_filename
        config = configparser.ConfigParser()
        if len ( config.read(ini_filename) ) == 0:
            raise FileNotFoundError("%s was not found" % ini_filename )
        sections = config.sections()
        self.hostname = os.environ["HOSTNAME"]
        if self.hostname not in sections:
            raise ValueError("hostname %s is not a section in the configuration file %s" % (self.hostname),
                             ini_filename )
        my_section = config[self.hostname]
        self.__ip_command = my_section['ip_command']

    @property  # Invoke this method when setting the name of the ip command.  On some machines, it is /sbin/ip
    # and on others it is /usr/sbin/ip or /usr/bin/ip
    def ip_command(self):
        """Return the name of the ip command"""

        return self.__ip_command

    @ip_command.setter
    def ip_command(self, name):
        raise NotImplementedError("You can't set the ip command programmatically.  You must modify file %s" % \
                                  self.__ini_filename)


if __name__ == "__main__":
    try:
        fixed_configuration = FixedConfiguration("XyZZy.txt")
    except FileNotFoundError as f:
        print("Raise FileNotFound error as expected", file=sys.stderr)
    else:
        print("The FixedConfiguration.__init__ method did *not* raise the FileNotFound exception as it should.")
    fixed_configuration = FixedConfiguration("nbmdt.ini")
    ip_command = fixed_configuration.ip_command

    try:
        fixed_configuration.ip_command="This should fail: calling the set_ip_command method"
    except NotImplementedError as n:
        print("fixed_configuration.set.ip_command failed as expected with NotImplementedError")
    else:
        print("EPIC FAIL!!! fixed_configuration.set_ip_command worked! Should have raised NotImplementedError")

    print(fixed_configuration.ip_command, fixed_configuration.hostname)