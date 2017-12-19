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
from termcolor import colored

PING_COMMAND = "/bin/ping"      # for now

class Tests():

    def __init__(self):
        self.my_resolver = dns.resolver.Resolver()


    @classmethod
    def ping4(cls, remote_ipv4:str, count:int=10, min_for_good:int=8, slow_ms:float=100.0 ):

        """This does a ping test of the machine remote_ipv4.
        :param  remote_ipv4     the remote machine to ping
        :param  min_for_good     The minimum number of successful pings required for the machine to be up
        :param  count           number of packets to be sent, default is 10
        :param  min_for_good    the number of packets that must be returned in order to consider the remote machine "up"
        :param  slow            The maximum amount of time, in milliseconds, that is allowed to transpire before the
                                remote machine will be considered "slow"

        """
        SLOW_MS = 100.0  # milliseconds.  This should be a configuration file option
        cpi = subprocess.run(args=[PING_COMMAND, '-n', count, remote_ipv4 ],
                             stdin=None,
                             input=None,
                             stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None,
                             check=False, encoding="utf-8", errors=None)
        if cpi.returncode != 0:
            raise subprocess.CalledProcessError
        # Because subprocess.run was called with encoding=utf-8, output will be a string
        results = cpi.stdout
        lines = results.split('\n')[:-1]  # Don't use the last element, which is empty

        """
        jeffs@jeffs-laptop:~/nbmdt (development)*$ ping -c 4  f5.com
        PING f5.com (104.219.110.168) 56(84) bytes of data.
        64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=1 ttl=249 time=24.0 ms
        64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=2 ttl=249 time=23.8 ms
        64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=3 ttl=249 time=23.3 ms
        64 bytes from 104.219.110.168 (104.219.110.168): icmp_seq=4 ttl=249 time=46.3 ms
        
        --- f5.com ping statistics ---
        4 packets transmitted, 4 received, 0% packet loss, time 3003ms
        rtt min/avg/max/mdev = 23.326/29.399/46.300/9.762 ms
        jeffs@jeffs-laptop:~/nbmdt (development)*$ 
        
        """
        for line in lines:
            if "transmitted " in line:
                packet_counters = re.findall("\d+.*?\d+")
                packets_xmit=packet_counters[0]
                packets_rcvd=packet_counters[1]
                down = packets_rcvd < min_for_good
            elif "rtt " == line[0:3]:         # crude, I will do something better, later
                # >>> re.findall("\d+\.\d+", "rtt min/avg/max/mdev = 23.326/29.399/46.300/9.762 ms")
                # ['23.326', '29.399', '46.300', '9.762']
                # >>>
                numbers = re.findall("\d+\.\d+", line)
                slow = numbers[1] > SLOW_MS
            else:
                pass

        return ( down, slow )

    @classmethod
    def ping6(cls, remote_ipv6:str, count:int=10, min_for_good:int=8, slow_ms:float=100.0 ):

        """This does a ping test of the machine remote_ipv6.
        :param  remote_ipv6     the remote machine to ping
        :param  min_for_good     The minimum number of successful pings required for the machine to be up
        :param  count           number of packets to be sent, default is 10
        :param  min_for_good    the number of packets that must be returned in order to consider the remote machine "up"
        :param  slow            The maximum amount of time, in milliseconds, that is allowed to transpire before the
                                remote machine will be considered "slow"

        """
        colored.cprint("ping6 isn't implemented yet", "yellow")
        return True


    def dns (self,  remote_host:str, dns_server:str=None ):     # type annotation should be str or list
        """This method tests that the name server DNS server can return queries and that it gets the right address for
        remote_host
        :param  dns_server  The name or IP address of the DNS server to test
        :param  remote_host     The name of the remote host to test.
        A future version might pass the "correct" answer
        """

        answer.response.answer[0]

        if dns_server is None:
            self.my_resolver.nameservers = ['8.8.8.8']
        elif isinstance( dns_server, list):
            self.my_resolver.nameservers = dns_server
        else:
            self.my_resolver.nameservers = [dns_server]

if __name__ == "__main__" :
    my_resolver = dns.ipv4
    answer = my_resolver.query('google.com')