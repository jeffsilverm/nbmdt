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
        self.config = configparser.ConfigParser()
        if len ( self.config.read(ini_filename) ) == 0:
            raise FileNotFoundError("%s was not found" % ini_filename )
        if False:
            sections = self.config.sections()
            self.hostname = os.environ["HOSTNAME"]
            if self.hostname not in sections:
                raise ValueError("hostname %s is not a section in the configuration file %s" % (self.hostname, self.__ini_filename))
            my_section = self.config[self.hostname]
            self.__ip_command = my_section['ip_command']
        return


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

    from routing import routing


    def make_test_nbmdt_ini_file():
        """Make a test ini file """
        routing = routing.Routes()
        default_gateway = routing.default_gateway()
        contents="""
[jeffs-laptop]
ping_targets: f5.com, commercialventvac.com, google.com
ping_command: /bin/ping
ip_command: /sbin/ip
default_gateway: 192.168.0.1

[jeffs-desktop]
ping_targets: f5.com, commercialventvac.com, google.com
ping_command: /bin/ping
ip_command: /sbin/ip
default_gateway: 192.168.8.1        

[jeffs_house]
ping_targets: f5.com, commercialventvac.com, google.com
ping_command: /bin/ping
ip_command: /sbin/ip
default_gateway: 192.168.0.1

[bad]
ping_targets:
        

        """
        with open("nbmdt.ini", mode="wt") as f:
            f.write(contents)
        return

# Main test program
    try:
        fixed_configuration = FixedConfiguration("XyZZy.txt")
    except FileNotFoundError as f:
        print("Raise FileNotFound error as expected", file=sys.stderr)

    make_test_nbmdt_ini_file()

    fixed_configuration = FixedConfiguration("nbmdt.ini")

    try:
        fixed_configuration.ip_command="This should fail: calling the set_ip_command method"
    except NotImplementedError as n:
        print("fixed_configuration.set.ip_command failed as expected with NotImplementedError")
    else:
        print("EPIC FAIL!!! fixed_configuration.set_ip_command worked! Should have raised NotImplementedError")
    ip_command = fixed_configuration.ip_command
    for section in fixed_configuration.sections():

        print(fixed_configuration[section].ip_command )
        ping_target_str = fixed_configuration[section]['ping_targets']
        ping_targets_list = ",".split(ping_target_str)
        for ping_target in ping_targets_list:
            print(f"In section {section} ping target is {ping}")



