#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Contains a class for applications and a class for DNS, which is an application

from termcolor import cprint as cprint
import sys
import constants
try:
    import dns
    from dns import resolver, rdatatype  # rdataclass,
except ImportError as i:
    print("Get package dns from nomium, install package 'dnspython'.  "
          "See dnspython DNS toolkit see http://www.dnspython.org/", file=sys.stderr)
    raise
from layer import Layer
from constants import ErrorLevels
import utilities
from typing import List, Dict
import typing

try:
    print("Testing the __file__ special variable: " + __file__, file=sys.stderr)
except Exception as e:  # if anything goes wrong
    print("Testing the __file__ special variable FAILED, exception is " + str(e), file=sys.stderr)


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
        if utilities.the_os == constants.OperatingSystems.LINUX:
            apps_str: str = utilities.OsCliInter.run_command(["ps", "-ax"])
            # Output from ps -ax command looks like (under linux)
            '''
              PID TTY      STAT   TIME COMMAND
        1 ?        Ss     0:00 /init ro
        3 tty1     Ss     0:00 /init ro
        4 tty1     S      0:00 -bash
      866 tty1     R      0:00 ps -ax
            '''
            apps_list: str = apps_str.split("\n")
            for app in apps_list:
                if "PID" in app:
                    continue
                ps_output = app.split()
                # When you get this right, DRY
                assert len(ps_output) == 5, "The length of ps_output is not 5.  ps_output is " + str(ps_output)
                pid, term, stat, time, command = app.split()
                d[pid] = Application(pid=pid, term=term, stat=stat, time=time, command=command)
        elif utilities.os == constants.OperatingSystems.WINDOWS:
            raise NotImplemented('in Applications.discover and operating system windows is not implemented yet')
        elif utilities.os == constants.OperatingSystems.MAC_OS_X:
            raise NotImplemented('in Applications.discover and operating system Mac OS X is not implemented yet')
        else:
            raise ValueError(f'in Applications.discover and utilities.os is {utilities.os} which is bad')
        return d

    def __init__(self, pid, term, stat, time, command) -> None:
        """

        :rtype: None
        """
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

class DNSFailure(Exception):

    # Eventually, I'd like a DNSFailure exception to include the name being looked
    # up and the kind of query being made.
    # Issue 12
    def __init__(self, name: str = None, query_type: str = 'A', *args) -> None:
        """
        :param name: str  The subject of the query
        :param query_type: str  The type of query.  Default is 'A', an IPv4 name query
        :param args:
        :param kwargs:
        """

        cprint(f"DNSFailure was raised querying {name} using query type {query_type}", 'red', file=sys.stderr)
        Exception.__init__(self, *args)


class DNS(object):

    def __init__(self):
        # self.resolvers = self.get_resolvers()
        self.resolver = dns.resolver.Resolver(configure=False)

    # Got this from https://github.com/donjajo/py-world/blob/master/resolvconfReader.py
    @classmethod
    def get_resolvers(cls: object) -> List[str]:
        """

        :rtype: List of strings.  Each string is the IP address (IPv4 or IPv6) of a resolver
        """
        resolvers = []
        try:
            # Known problem: /etc/resolv.conf is Linux or UNIX specific.  Apparently
            with open('/etc/resolv.conf', 'r') as resolvconf:
                for line in resolvconf.readlines():
                    line = line.split('#', 1)[0]
                    line = line.rstrip()
                    if 'nameserver' in line:
                        resolvers.append(line.split()[1])
        except IOError as error:
            cprint(f"Raised an IOError exception {error.strerror}", 'white', 'on_red', file=sys.stderr)
        return resolvers

    def query_specific_nameserver(self, server_list: list, qname: str, rdatatype_enm: dns.rdatatype):
        """
        Query a specific nameserver for a translation.  If this nameserver fails, then this call fails.  By way of
        contrast, gethostbyname and socket will automatically retry a different nameservers
        :type rdatatype_enm: a dns.rdatatype constant that describes the type of query.  Examples of values include
                dns.rdatatype.A, dns.rdatatype.AAAA, dns.rdatatype.PTR, dns.rdatatype.MX, ...
        :param server_list: A list of servers (possibly length 1) to query
        :param qname:   The thing to query for
        :param rdatatype_enm:   The kind of queries to make
        :return: A list of answers
        """

        self.resolver.nameservers = server_list
        assert isinstance(rdatatype_enm, dns.rdatatype), f"The type of rdatatype is {type(rdatatype_enm)} should be " +\
                                                         str(type(dns.rdatatype))
        answer: list = dns.resolver.query(qname, rdatatype_enm)
        answer.sort()
        return answer


class Web(object):
    """
    Monitors a web server
    """
    pass


if __name__ == "__main__":
    # This should be moved to a file in test, test_application.py
    raise NotImplemented
