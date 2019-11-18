#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Contains a class for applications and a class for DNS, which is an application

import sys
import typing
from typing import List, Dict

import dns.rdatatype  # rdataclass,
# dnspython DNS toolkit see http://www.dnspython.org/
import dns.resolver
from termcolor import cprint as cprint

import utilities
from constants import ErrorLevels
from layer import Layer


class Application(object):

    @classmethod
    def discover(cls) -> typing.Dict[str, 'Application']:
        """
        Use an operating system command to build a dictionary of applications.  The operating system is key'd by
        PID (which wouldn't work if there was an OS that didn't have PIDs).  The value of the the dictionary is an
        Application object.  The interior of an application is OS dependent
        :return:
        """
        d: Dict[str, cls] = {}
        if 'Linux' == utilities.OsCliInter.system:
            apps_str: str = utilities.OsCliInter.run_command(["ps", "-ax"])
            # Output from ps -ax command looks like (under linux)
            '''
              PID TTY      STAT   TIME COMMAND
        1 ?        Ss     0:00 /init ro
        3 tty1     Ss     0:00 /init ro
        4 tty1     S      0:00 -bash
      866 tty1     R      0:00 ps -ax
            '''
            apps_list: List[str] = apps_str.split("\n")
            for app in apps_list:
                if "PID" in app:
                    continue
                pid, term, stat, time, command = app.split()
                d[pid] = cls.__init__(pid=pid, term=term, stat=stat, time=time, command=command)
        elif 'Windows' == utilities.OsCliInter.system():
            raise NotImplemented('in Applications.discover and system windows is not implemented yet')
        else:
            raise ValueError(f'in Applications.discover and system {utilities.OsCliInter.system()} is strange')
        return d

    def __init__(self, pid, term, stat, time, command) -> None:
        self.layer = Layer()
        self.pid = pid
        self.term = term
        self.stat = stat
        self.time = time
        self.command = command

    def get_status(self) -> ErrorLevels:
        return self.layer.get_status()

    def __str__(self):
        return "Application __str__ method"


# DNS sits at the application layer in the OSI model, according to
# https://en.wikipedia.org/wiki/List_of_network_protocols_(OSI_model)
# But since DNS is useful at many different levels in the stack, I am moving
# the DNSFailure exception class from here to utilities.py
# https://github.com/jeffsilverm/nbmdt/issues/40
class DNS(object):

    def __init__(self):
        self.get_resolvers()
        self.resolver = dns.resolver.Resolver(configure=False)

    # Got this from https://github.com/donjajo/py-world/blob/master/resolvconfReader.py
    @staticmethod
    def get_resolvers(self):
        resolvers = []
        try:
            with open('/etc/resolv.conf', 'r') as resolvconf:
                for line in resolvconf.readlines():
                    line = line.split('#', 1)[0]
                    line = line.rstrip()
                    if 'nameserver' in line:
                        resolvers.append(line.split()[1])
        except IOError as error:
            cprint(f"Raised an IOError exception {error.strerror}", 'white', 'on_red', file=sys.stderr)
            self.resolvers = []
        self.resolvers = resolvers

    # Issue 40 https://github.com/jeffsilverm/nbmdt/issues/40
    # The method query_specific_nameserver was here, now moved to utilities.py


class web(object):
    """
    Monitors a web server
    """
    pass


if __name__ == "__main__":
    # Issue 40
    pass
