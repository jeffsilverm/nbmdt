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

class FixedConfiguration( object ):
    """
    An object of FixedConfiguration has the read-only configuration for nbmdt
    """

    hostname = os.environ['HOSTNAME']

    def __init__(self, ini_filename: str, machine_name: str ):
        """
        This method creates a FixedConfiguration object from the file ini_filename
        :param ini_filename:  str
        """
        global hostname

        config = configparser.ConfigParser()
        config.read(ini_filename)
        sections=config.sections()
        self._ip_command=sections[hostname]['ip_command']
        self._ini_filename=ini_filename


    @property           # Invoke this method when setting the name of the ip command
    def get_ip_command(self):
        """Return the name of the ip command"""

        return self.hostname

    @_ip_command.setter  # when you do Stock.name = x, it will call this function
    def set_ip_command(self, name):
        raise NotImplementedError("You can't set the hostname programmatically.  You must modify file %s" % \
                                  self._ini_filename)

if __name__ == "__main__":
    fixed_configuration = FixedConfiguration("nmbd.ini")
    ip_command = fixed_configuration.get_ip_command()

    try:
        fixed_configuration.set_ip_command("This should fail")
    except NotImplementedError as n:
        print("fixed_configuration.set_ip_command failed as expected with NotImplementedError")
    else:
        print("EPIC FAIL!!! fixed_configuration.set_ip_command worked! Should have raised NotImplementedError")


    try:
        fixed_configuration._ip_command="This should fail"
    except NotImplementedError as n:
        print("fixed_configuration._ip_command failed as expected with NotImplementedError")
    else:
        print("EPIC FAIL!!! fixed_configuration._ip_command worked! Should have raised NotImplementedError")

