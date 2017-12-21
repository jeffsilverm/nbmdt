#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool
#
"""
This module contains various tests for things
ping test
TCP connectivity
UDP - if I can figure out how to do some sort of general UDP connectivity
DNS reachability
DNS ability to resolve a query
HTTP connectivity with a known status return

for both IPv4 and IPv6

"""

import termcolor
import subprocess
import re
# Get dns from https://github.com/rthalley/dnspython
import dns.resolver
import sys
import socket       # Required for testing the Tests.dns method
from termcolor import colored



class Tests(object):

    def __init__(self):
        self.my_resolver = dns.resolver.Resolver()



        # type annotation should be str or list
    def dns (self,  remote_host:str, dns_server:str=None):     # type annotation should be str or list
        """This method tests that the name server DNS server can return queries and that it gets the right address for
        remote_host
        :param  dns_server  The name or IP address of the DNS server to test.  This might be a single name server, in
                            which case, it will be a string.  This might be a list of name servers, in which case, it will
                            be a list of strings
        :param  remote_host     The name of the remote host to test.
        A future version might pass the "correct" answer
        """


        if dns_server is None:
            # This is not the right way to do it.  The right way to do it would be to query /etc/resolv.conf and get
            # the list of nameservers.  Also, this only works for IPv4.
            self.my_resolver.nameservers = ['8.8.8.8']
        elif isinstance( dns_server, list):
            self.my_resolver.nameservers = dns_server
        else:
            self.my_resolver.nameservers = [dns_server]

        answer = self.my_resolver.query(remote_host)
        print( answer.response.answer[0], file=sys.stderr)
        return answer.response.answer[0]


if __name__ == "__main__":
    def test_dns ( remote_host, dns_server=None ):
        """This method tests the dns method by comparing what it returns against what gethostbyname returns.
        Returns true if correct"""
        correct = socket.gethostbyname(remote_host)
        tests = Tests()
        if dns_server is None:
            test_answer = tests.dns(remote_host, dns_server)
            my_answer = test_answer.items.O.address
            print(f"'Correct' answer: {correct}.  My answer {my_answer}", file=sys.stderr)
            return my_answer == test_answer
        else:
            with open("/etc/resolv.conf","r") as f:
                configuration=f.readlines()
            ns_list=[]
            for l in configuration:
                if "nameserver" in l:
                    ns_list.append(l.split()[1])
            for dns_server in ns_list:
                try:
                    test_answer = tests.dns(remote_host, dns_server)
                except Exception as e:
                    print(f"tests.dns raised the {str(e)} exception on nameserver {dns_server}  Retrying", file=sys.stderr)
                    test_answer = None
                    continue
            return correct == test_answer

    for remote_host in ['jeffsilverman.com', 'f1.com', 'commercialventvac.com']:
        for nameserver in [None, "8.8.8.8", "2001:4860:4860::8888", "2001:4860:4860::8884"  ]:
            assert test_dns(remote_host, nameserver ), f"{remote_host} failed with nameserver {'default' if nameserver is None else nameserver} "




