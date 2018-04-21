#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Contains a class for applications and a class for DNS, which is an application

from termcolor import cprint as cprint
import sys
# dnspython DNS toolkit
import dns
from dns import resolver, rdatatype  # rdataclass,
from layer import Layer
from constants import ErrorLevels

class Application(object):

    def discover(self):
        pass

    def __init__(self):
        self.layer = Layer()

    def get_status(self)  -> ErrorLevels:
        return self.layer.get_status()


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

    def query_specific_nameserver(self, server_list: list, qname: str, rdatatype: str):
        """

        :param server_list: A list of servers (possibly length 1) to query
        :param qname:   The thing to query for
        :param rdatatype:   The kind of queries to make
        :return: A list of answers
        """

        self.resolver.nameservers = server_list
        answer: list = dns.resolver.query(qname, rdatatype)
        answer.sort()
        return answer


class web(object):
    """
    Monitors a web server
    """
    pass


if __name__ == "__main__":

    def resolver_tst():
        answer = dns.query_specific_nameserver(resolver, rdatatype)
        for rr in answer:
            print(f"  {rr}")
            if rr not in ['172.217.3.46']:
                pass

        okay = True
        answer = dns.query_specific_nameserver(server_list=[resolver],
                                               qname="google.com",
                                               rdatatype=rdatatype.AAAA)
        for rr in answer:
            print(f"  {rr}")
            if rr not in ["2607:f8b0:4008:80d::200e",
                          '2607:f8b0:4004:811::200e']:
                cprint(
                        f"server {resolver} returned unanticipated IPv6 answer rr",
                        'yellow')
                okay = False
        return okay


    dns = DNS()
    cprint(f"Testing local DNS resolvers from /etc/resolv.conf", "blue", file=sys.stderr)
    local_resolvers = dns.get_resolvers()
    print(local_resolvers)
    failed_resolver_list = []
    for resolver in local_resolvers + ['8.8.8.8']:
        print(40 * '=' + '\n' + f"Working on resolver {resolver}")
        okay = resolver_tst(resolver=resolver, qname="google.com", rdatatype=rdatatype.A)
        if not okay:
            failed_resolver_list.append(resolver)
            cprint(f"Resolver {resolver} failed the IPv4 test.", 'red')
        all_okay = all_okay and okay
        okay = resolver_tst(resolver=resolver, qname="google.com", rdatatype=rdatatype.AAAA)
        if not okay:
            failed_resolver_list.append(resolver)
            cprint(f"Resolver {resolver} failed the IPv6 test.", 'red')
        all_okay = all_okay and okay
    if len(failed_resolver_list) == 0:
        cprint("All resolvers pass IPv4 checks", 'green')
    else:
        cprint(f"Some resolvers failed.  They are:{failed_resolver_list}", 'red')

    cprint(f"Testing a non-existant resolver", 'blue', file=sys.stderr)
    okay = resolver_tst(resolver=['192.168.0.143'], qname="google.com", rdatatype=rdatatype.A)