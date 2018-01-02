#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module is responsible for representing the routing tables.  There are at least 2: one for IPv4 and one for IPv6
import socket
import subprocess
import sys
import re
from applications import DNSFailure
from typing import Union
from termcolor import colored, cprint
from configuration import Configuration

# The color names described in https://pypi.python.org/pypi/termcolor are:
# Text colors: grey, red, green, yellow, blue, magenta, cyan, white
# Text highlights: on_grey, on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white

IP_COMMAND = Configuration.find_executable('ip')
PING_COMMAND = Configuration.find_executable('ping')
PING6_COMMAND = Configuration.find_executable('ping6')
cprint(f"Debugging network.py: {IP_COMMAND}, {PING_COMMAND}, {PING6_COMMAND}", 'green', file=sys.stderr)

class NotPingable(Exception):
    def __init__(self, name : str = None) -> None:
        cprint (f"{name} is not pingable", 'yellow', file=sys.stderr)
    pass


# Issue 5 renamed IPv4_address to IPv4Address.   Reflecting what PEP-8 says
class IPv4Address(object):
    """
    This object has an IPv4 object.  It has two attributes: name and ipv4_address.
    If the name has not been specified, then it is None
    """

    def __init__(self, name : str = None, ipv4_address : Union[str, bytes] = None) -> None :
        """
        :param name:    str remote computer name
        :param ipv4_address: str remote computer name as a dotted quad (e.g. 192.168.0.1) or as a 4 bytes
        :raises ValueError
        """
        def raise_value_error (name, ipv4_address):
            raise ValueError("Create an IPv4Address object with either a name or an IPv4 address but not both "\
                             f"{name} and {ipv4_address} .")

        self.ipv4_subnet_mask = 0      # This is the default unless the name is a dotted quad IPv4 address with a
                                            # subnet mask length
        if name is not None:
            if name == "default":
                # I think is the true resolution of Issue 10
                """
    >>> addr2=sk.inet_aton( "0.0.0.0")
    >>> addr2
    b'\x00\x00\x00\x00'
    >>> 
                """
                self.name = "0.0.0.0"
            elif "/" in name :
                parts = name.split("/")
                self.name = parts[0]
                # This is the only case where the ipv4_subnet_mask might be other than 0
                self.ipv4_subnet_mask = int( parts[1] )
            elif isinstance(name, tuple):
                if len(name) == 3 and isinstance(name[0], str) and isinstance(name[2], list):
                    # This looks strange.  However, in some cases, the name is actually a 3-tuple where element 0 is the name
                    # as a Unicode string, element 1 is an empty list (Why?  I ought to know), and element 2 is a list of
                    # length 1 which has the IPv4 address of the host
                    self.name = name[0]
                    self.ipv4_address = socket.inet_aton(name[2][0])
                else :
                    raise ValueError("Tried to create an IPV4Address object "\
                        "with a name that was a tuple but was either not length 3, the first element was not a string,"\
                        " or the third element was not a list")
            else :
                self.name = name
                # This might raise a socket.gaierror exception, but at this point, there's not much that can be done.
                self.ipv4_address = socket.inet_aton( socket.gethostbyname(name) )
            if ipv4_address is None:
                # The exception described by Issue 10 starts here.  Just because gethostbyname fails, doesn't mean we
                # work with the name.  It might have an IPv4 address in it in dotted quad format.
                # For example:
                """
Python 3.6.1 (default, Sep  7 2017, 16:36:03) 
[GCC 6.3.0 20170406] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> name="f5.com"
>>> import socket as sk
>>> addr=sk.inet_aton( sk.gethostbyname(name) )
>>> addr
b'h\xdbn\xa8'
>>> addr2=sk.inet_aton( "104.219.110.168" )
>>> addr2
b'h\xdbn\xa8'
>>> addr == addr2
True
>>>
                """
                try:
                    self.ipv4_address = socket.inet_aton( socket.gethostbyname(self.name) )
                except socket.gaierror as g:
                    # Now, if this call to inet_aton fails, then it's hopeless
                    self.ipv4_address = socket.inet_aton( name )

            else:
                raise_value_error(name, ipv4_address)
        elif ipv4_address is not None:      # and name is None
            # Because we're here, we know that we have to populate the self.ipv4_address and self.name attributes from
            # the ipv4_address we were given.
            # socket.inet_aton(ip_string) will create a packed IPv4 address from a dotted quad string
            # socket.gethostbyaddr(ip_string) must have a dotted quad string
            # If we were given a packed IPv4 address, then it must be converted to dotted quad string before we can
            # call gethostbyaddr.
            # https://docs.python.org/3/library/socket.html#socket.inet_pton
            # if ipv4 is malformed, then inet_pton will raise an error
            s = isinstance(ipv4_address, str)
            b = isinstance(ipv4_address, bytes) and ( len(ipv4_address) == 4 )
            if not ( s or b ):
                raise ValueError(
                    f"ipv4_address is {ipv4_address}, type {type(ipv4_address)} of length {len(ipv4_address)} " \
                    " but should be either str or 4 byte array")
            try:
                if b:
                    # It is a packed IPv4 address, so use it, but unpack it
                    self.ipv4_address = ipv4_address
                    ipv4_address = socket.inet_ntoa(ipv4_address)
                if s:
                    self.ipv4_address = socket.inet_aton(ipv4_address)
                self.name = socket.gethostbyaddr(ipv4_address)
            # At this point, self.ipv4_address must be populated, but self.name might not be if the gethostbyaddr call failed
            # Also, at this point, ipv4_address is a dotted quad string
            except ( socket.herror, socket.gaierror )  as e:
                cprint("socket.gethostbyaddr raised an "
                       "exception on %s, continuing" % ipv4_address, 'yellow',
                       file=sys.stderr)
                self.name = ipv4_address

        else:
            # Both name and ipv4_address are None
            raise_value_error(name, ipv4_address)
        # Now, fix up a little wrinkle from gethostbyaddr.  self.name should be a string, but depending on how it was
        # created, it might be a string or, from https://docs.python.org/3/library/socket.html?highlight=socket%20inet_pton#socket.gethostbyaddr,
        # it might be a tuple of the (hostname, aliaslist, ipaddrlist) where hostname is the primary host name corresponding to the given
        # ip_address, aliaslist is a(possibly empty) list of alternative host names for the same address, and ipaddrlist is a list of
        # IPv4 / v6 addresses for the same interface on the same host (most likely containing only a single address).
        if isinstance ( self.name, tuple) and len ( self.name ) == 3 and isinstance ( self.name[1], list) and isinstance ( self.name[2], list) :
            self.name = self.name[0]
        elif not isinstance ( self.name, str ):
            raise AssertionError(f"self.name should be either a 3-tuple or a string, but its really a {type(self.name)}.  "\
                                 f"It's {self.name}.  In the IPv4Address constructor with name={name} and ipv4_address={ipv4_address}")
        else:
            pass        # already a string
        # Some sanity checks to make sure I haven't introduced any bugs
        assert hasattr(self,'ipv4_address'), \
            f'At the end of the IPv4Address constructor with {self.name}, '\
                f'there is no ipv4_address attribute. name={name}, ipv4_address={ipv4_address}'
        assert hasattr(self,'name'), \
            f'At the end of the IPv4Address constructor with {self.ipv4_address}, '\
                f'there is no name attribute. name={name}, ipv4_address={ipv4_address}'
        assert isinstance(self.name, str), \
            f'At the end of the IPv4Address constructor, self.name is type {type(self.name)}'\
                f'should be str.  name={name}, ipv4_address={ipv4_address}'
        assert isinstance(self.ipv4_address, bytes), \
            f'At the end of the IPv4Address constructor, self.ipv4_address is type {type(self.ipv4_address)}' \
            f'should be str.  name={name}, ipv4_address={ipv4_address}'
        # This is a constructor, so don't return anything or return None

    def validate(self) -> str:
        """
        :return:    Either False or None if this IPv4Address object is valid or else a diagnostic string
        """



    def __str__(self):
        # https://docs.python.org/3/library/socket.html#socket.inet_ntop
        ipv4_addr_str = socket.inet_ntop(socket.AF_INET, self.ipv4_address)
        return ipv4_addr_str

    def ping4(self, count: str = "10", min_for_good: int = 8, slow_ms: float = 100.0, production=True) -> tuple:
        """This does a ping test of the machine with this IPv4 address
        :param  self            the remote machine to ping
        :param  min_for_good     The minimum number of successful pings required for the machine to be up
        :param  count           number of packets to be sent, default is 10
        :param  min_for_good    the number of packets that must be returned in order to consider the remote machine "up"
        :param  slow_ms         The maximum amount of time, in milliseconds, that is allowed to transpire before the
                                remote machine will be considered "slow"
        :param  production      If production is false, then ping4 won't raise a NotPingable exception
        :return     Returns a 2-tuple.  This first element is True if pingable, number of good pings >= min_for_good
                                The second element is True if the average response time (milliseconds) is >= slow_ms
        """

        SLOW_MS = 100.0  # milliseconds.  This should be a configuration file option
        name = str(self)
        # Issue 11 starts here https://github.com/jeffsilverm/nbmdt/issues/11
        # -c is for linux, use -n for windows.
        cpi = subprocess.run(args=[PING_COMMAND, '-c', count, name ],
                             stdin=None,
                             input=None,
                             stdout=subprocess.PIPE, stderr=None,
                             shell=False, timeout=None,
                             check=False, encoding="utf-8", errors=None)
        # return status = 0 if everything is okay
        # return status = 2 if DNS fails to look up the name
        # return status = 1 if the device is not pingable
        if cpi.returncode == 2:
            raise DNSFailure(name=name, query_type='A')
        elif cpi.returncode != 0 and cpi.returncode !=1 :
            cprint(f"About to raise a subprocess.CalledProcessError exception. name={name} cpi={cpi} returncode is {cpi.returncode}",
                   'red', file=sys.stderr)
            raise subprocess.CalledProcessError
        elif cpi.returncode == 1 and production:
            raise NotPingable( name= name )
        else:
            # Because subprocess.run was called with encoding=utf-8, output will be a string
            results = cpi.stdout
            lines = results.split('\n')[:-1]
                  # Don't use the last element, which is empty
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
            # Failsafe initialization
            slow : bool = True
            up : bool = cpi.returncode == 0
            # loop through output of ping command
            for line in lines:
                if "transmitted" in line:
                    # re.findall returns a list of length 1 because there is 1 match to the RE
                    packet_counters = \
                    re.findall("(\d+).*?(\d+).*received.*(\d+).*()", line)[0]
                    packets_xmit = packet_counters[0]
                    packets_rcvd = packet_counters[1]
                    # If at least one packet was received, then the remote machine
                    # is pingable and the NotPingable exception will not be raised
                    up = int(packets_rcvd)  >= min_for_good
                elif "rtt " == line[0:4]:  # crude, I will do something better, later
                    # >>> re.findall("\d+\.\d+", "rtt min/avg/max/mdev = 23.326/29.399/46.300/9.762 ms")
                    # ['23.326', '29.399', '46.300', '9.762']
                    # >>>
                    # The RE matches a fixed point number, and there are 4 of them.  The second one is the average
                    numbers = re.findall("\d+\.\d+", line)
                    slow = float(numbers[1]) > slow_ms
                else:
                    pass
            cprint(f"About to exit from ping4 up={up} slow={slow}", 'yellow')
            return (up, slow)


# Issue 5 renamed IPv6_address to IPv6Address
class IPv6Address(object):
    def __init__(self, name : str = None, ipv6_address : Union[str, bytes ] = None ) -> None:
        """
        :param name:    str remote computer name
        :param ipv6_address: str remote computer name or byte string
        :raises ValueError
        """

        if name is not None:
            self.name = name
        # Needs work
        self.ipv6_address = ipv6_address

    def ping6(self, count:int=10, min_for_good:int=8, slow_ms:float=100.0 ):

        """This does a ping test of the machine remote_ipv6.
        :param  self          the remote machine to ping
        :param  min_for_good     The minimum number of successful pings required for the machine to be up
        :param  count           number of packets to be sent, default is 10
        :param  min_for_good    the number of packets that must be returned in order to consider the remote machine "up"
        :param  slow            The maximum amount of time, in milliseconds, that is allowed to transpire before the
                                remote machine will be considered "slow"

        """
        cprint("ping6 isn't implemented yet", "yellow")
        return True



class IPv4Route(object):
    """
    A description of an IPv4 route

        :type ipv4_use: object
        
jeffs@jeff-desktop:~/Downloads/pycharm-community-2017.1.2 $ ip -4 route list
default via 192.168.0.1 dev eno1 
10.0.3.0/24 dev lxcbr0  proto kernel  scope link  src 10.0.3.1 linkdown 
169.254.0.0/16 dev br-ext  proto static  scope link  metric 425 linkdown 
192.168.0.0/24 dev eno1  proto kernel  scope link  src 192.168.0.7 
192.168.0.0/22 dev br-ext  proto kernel  scope link  src 192.168.3.50  metric 425 linkdown 
192.168.122.0/24 dev virbr0  proto kernel  scope link  src 192.168.122.1 linkdown 
jeffs@jeff-desktop:~/Downloads/pycharm-community-2017.1.2 $ 
        


    
    """

    default_ipv4_gateway = None

    def __init__(self, route ):
        """This returns an IPv4Route object.  """

 # Use caution: these are strings, not length 4 bytes
        self.ipv4_destination = route['ipv4_destination']  # Destination must be present
        self.ipv4_subnet_mask = 0               # This is the default
        self.ipv4_dev = route['dev']
        self.ipv4_gateway = route.get('via', None)
        self.ipv4_proto = route.get('proto', None)
        self.ipv4_scope = route.get('scope', None )
        self.ipv4_metric = route.get('metric', 0 )
        self.ip4v_src = route.get('src', None )
        self.ipv4_linkdown  = route.get('linkdown', False )
        assert isinstance( self.ipv4_linkdown, bool ),\
            "linkdown is not a boolean, its %s" % type(self.ipv4_linkdown)


    @classmethod
    def find_ipv4_routes(cls):
        """This method finds all of the IPv4 routes by examining the output of the ip route command, and
        returns a list of IPV4_routes.  This is a class method because all route objects have the same
         default gateway"""

        def translate_destination(destination: str) -> str:
            """
This method translates destination from a dotted quad IPv4 address to a name if it can"""
            if destination == "0.0.0.0" or destination == "default":
                name = "default"
            else:
                try:
                    name = socket.gethostbyaddr(destination)[0]
                except ( socket.herror, socket.gaierror ) as h:
                    # This exception will happen, because the IPv4 addresses in the LAN are probably not in DNS or in
                    # /etc/hosts.  Now, should I print the message, even though I expect it?
                    # says that it can so I have to handle it
                    cprint("socket.gethostbyaddr raised an "
                          "exception on %s, continuing" % destination, 'yellow',
                          file=sys.stderr)
                    name = destination
                else:
                    pass
            return name

        # https://docs.python.org/3/library/subprocess.html
        cpi = subprocess.run(args=[IP_COMMAND, '-4', 'route', 'list'],
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
jeffs@jeffs-desktop:~/nbmdt (blue-sky)*$ ip -4 route
default via 192.168.0.1 dev eno1 proto static metric 100 
10.0.3.0/24 dev lxcbr0 proto kernel scope link src 10.0.3.1 linkdown 
169.254.0.0/16 dev eno1 scope link metric 1000 
192.168.0.0/24 dev eno1 proto kernel scope link src 192.168.0.16 metric 100 
192.168.122.0/24 dev virbr0 proto kernel scope link src 192.168.122.1 linkdown 
jeffs@jeffs-desktop:~/nbmdt (blue-sky)*$ 

        """

        route_list = list()
        cls.default_ipv4_gateway = None
        for line in lines:      # lines is the output of the ip route list
            # command
            fields = line.split()
            destination : str = translate_destination(fields[0])

            route=dict()
            try:
                route['ipv4_destination'] = IPv4Address(destination)
            except socket.gaierror as g:
                cprint(f"Tried to add the destination {destination} to a route, and a socket.gaierror exception was raised", 'red', file=sys.stderr )
            except OSError as o:
                cprint(f"Tried to add the destination {destination} to a route, and an OSError exception was raised", 'red', file=sys.stderr )

            for i in range(1, len(fields), 2):
                if fields[i] == 'linkdown':
                    route['linkdown'] = True
                    break
                # A string that identifies the value that follows it.
                route[fields[i]] = fields[i+1]
            ipv4_route = IPv4Route( route=route )
            if destination == "default" or destination == "0.0.0.0":
                cls.default_ipv4_gateway = IPv4Address(ipv4_route.ipv4_gateway)
            route_list.append(ipv4_route)

        return route_list

    def __str__(self):
        """This method produces a nice string representation of a IPv4_route object"""
        return f"dest={self.ipv4_destination} mask={self.ipv4_subnet_mask}, gateway={self.ipv4_gateway} " \
               f"dev={self.ipv4_dev} " \
               f"metric={self.ipv4_metric} proto={self.ipv4_proto} "\
               f"src={self.ip4v_src} scope={self.ipv4_scope} " + \
               ( "linkdown" if self.ipv4_linkdown else "linkUP" )

    @classmethod
    def get_default_ipv4_gateway(cls) -> IPv4Address:
        """Returns the default gateway.  If the default gateway attribute does not exist, then this method ought to
        invoke find_ipv4_routes, which will define the default gateway"""
        if not hasattr(cls, "default_ipv4_gateway") or cls.default_ipv4_gateway is None:
            # This has some overhead, and ought to be cached somehow.  Deal with that later.
            cls.find_ipv4_routes()
        assert cls.default_ipv4_gateway is not None, 'The default IPv4 gateway is not defined at the end of get_default_ipv4_gateway'
        return cls.default_ipv4_gateway


class IPv6Route(object):
    def __init__(self, ipv6_destination, ipv6_next_hop, ipv6_proto, ipv6_interface, ipv6_metric):

        self.ipv6_destination = ipv6_destination
        self.ipv6_next_hop = ipv6_next_hop
        self.ipv6_metric = ipv6_metric
        self.ipv6_interface = ipv6_interface
        self.ipv6_proto = ipv6_proto

    def __str__(self):
        """This method produces a nice string representation of a IPv4_route object"""
        return f"dest={self.ipv6_destination} gateway={self.ipv6_next_hop} " \
               f"dev={self.ipv6_interface} " \
               f"metric={self.ipv6_metric} proto={self.ipv6_proto} "


    @classmethod
    def find_ipv6_routes(cls):
        """This method returns an IPv6 routing table.  In version 1, this is done by running the route command and
        scrapping the output.  A future version will query the routing table through the /sys pseudo file system"""

        # jeffs@jeff-desktop:~ $ ip --family inet6 route show
        # 2601:602:9802:93a8::/64 dev eno1  proto kernel  metric 256  expires 1583sec pref medium
        # 2601:602:9802:93a8::/64 dev enp3s0  proto kernel  metric 256  expires 1583sec pref medium
        # fe80::/64 dev eno1  proto kernel  metric 256  pref medium
        # fe80::/64 dev enp3s0  proto kernel  metric 256  pref medium
        # default via fe80::2e30:33ff:fe55:ca5f dev eno1  proto ra  metric 1024  expires 1317sec hoplimit 64 pref low
        # default via fe80::2e30:33ff:fe55:ca5f dev enp3s0  proto ra  metric 1024  expires 1317sec hoplimit 64 pref low
        # jeffs@jeff-desktop:~ $

        #        jeffs @ jeff - desktop: ~ $ python3
        #        Python
        #        3.5
        #        .2(default, Nov
        #        17
        #        2016, 17: 05:23)
        #        [GCC 5.4.0 20160609]
        #        on
        ###        linux
        #        Type
        #        "help", "copyright", "credits" or "license"
        #        for more information.
        #            >> > import subprocess
        #        >> > c = subprocess.run(["/sbin/ip", "--family", "inet6", "route", "show", "all"], stdin=None, input=None,
        #                                stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        #        >> > c.stdout.decode('utf-8')
        #        'default via fe80::2e30:33ff:fe55:ca5f dev eno1  proto ra  metric 1024  expires 1653sec hoplimit 64 pref low\ndefault via fe80::2e30:33ff:fe55:ca5f dev enp3s0  proto ra  metric 1024  expires 1653sec hoplimit 64 pref low\n'
        #        >> > c = subprocess.run(["/sbin/ip", "--family", "inet6", "route", "show"], stdin=None, input=None,
        #                                stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        #        >> > c.stdout.decode('utf-8')
        #        '2601:602:9802:93a8::/64 dev eno1  proto kernel  metric 256  expires 2086sec pref medium\n2601:602:9802:93a8::/64 dev enp3s0  proto kernel  metric 256  expires 2086sec pref medium\nfe80::/64 dev eno1  proto kernel  metric 256  pref medium\nfe80::/64 dev enp3s0  proto kernel  metric 256  pref medium\ndefault via fe80::2e30:33ff:fe55:ca5f dev eno1  proto ra  metric 1024  expires 1680sec hoplimit 64 pref low\ndefault via fe80::2e30:33ff:fe55:ca5f dev enp3s0  proto ra  metric 1024  expires 1680sec hoplimit 64 pref low\n'
        #       >> >
        #

        # This is the recommend approach for python 3.5 and later  From https://docs.python.org/3/library/subprocess.html
        completed = subprocess.run(["/sbin/ip", "--family", "inet6", "route", "show"], stdin=None, input=None, \
                                   stdout=subprocess.PIPE, stderr=None,
                                   shell=False, timeout=None, check=False,
                                   encoding="ascii",
                                   errors=None)
        """
        jeffs@jeffs-desktop:/home/jeffs/logbooks/work  (master) *  $ /sbin/ip --family inet6 route show
2602:61:7e44:2b00::/64 via fe80::6bf:6dff:fed9:8ab4 dev eno1 proto ra metric 100  pref medium
fd00::/64 via fe80::6bf:6dff:fed9:8ab4 dev eno1 proto ra metric 100  pref medium
fe80::6bf:6dff:fed9:8ab4 dev eno1 proto static metric 100  pref medium
fe80::/64 dev eno1 proto kernel metric 256  pref medium
default via fe80::6bf:6dff:fed9:8ab4 dev eno1 proto static metric 100  pref medium
jeffs@jeffs-desktop:/home/jeffs/logbooks/work  (master) *  $ 
        """
        route_list = []
        for r in completed.stdout.split('\n'):
            if len(r) <= 0:             # There may be an empty line at the end
                break
            fields:list = r.split()
            ipv6_destination = fields[0]
            if fields[1] == "via":
                ipv6_next_hop = fields[2]
                start = 3
            elif fields[1] == "dev":
                ipv6_next_hop = None
                start = 1
            else:
                raise ValueError(f"fields[1] has a bad value {fields[1]} should be either 'via' or 'dev'.\nLine is {r}")
            if fields[start] != "dev":
                raise ValueError(f"fields[{start}] should be 'dev' but is actually {fields[start]}.\nLine is {r}")
            ipv6_interface = fields[start+1]
            if fields[start+2] != "proto":
                raise ValueError(f"field[{start+2}] should be 'proto' but is actually {fields[start+2]}.\nLine is {r}")
            ipv6_proto = fields[start+3]
            if fields[start+4] != "metric":
                raise ValueError(f"field[{start+4}] should be 'metric' but is actually {fields[start+4]}.\nLine is {r}")
            ipv6_metric = fields[start+5]
            if fields[start+6] != "pref" :
                raise ValueError(f"field[{start+7}] should be 'pref' but is actually {fields[start+6]}.\nLine is {r}")
            route_table_entry = IPv6Route(ipv6_destination=ipv6_destination,
                                          ipv6_next_hop=ipv6_next_hop,
                                          ipv6_proto=ipv6_proto,
                                          ipv6_interface=ipv6_interface,
                                          ipv6_metric=ipv6_metric
                                          )
            route_list.append(route_table_entry)
            if ipv6_destination == "default":
                cls.default_ipv6_gateway = ipv6_destination

        if not hasattr(cls, "default_ipv6_gateway" ):
            # Have to think about this - what action should be taken if there is no
            # default gateway?
            cls.default_ipv6_gateway = None

        return route_list

    @classmethod
    def get_default_ipv6_gateway(cls):
        """Returns the default gateway.  If the default gateway attribute does not exist, then this method ought to
        invoke find_ipv6_routes, which will define the default gateway"""
        if not hasattr(cls, "default_ipv6_gateway"):
            # This has some overhead, and ought to be cached somehow.  Deal with that later.
            cls.find_ipv6_routes()
        # Issue 14
        assert isinstance(cls.default_ipv6_gateway, cls.IPv6Address), \
            f"In network.IPv6Route.get_default_ipv6_gateway will return a {type(cls.default_ipv6_gateway)}, " \
            "should have returned a network.IPv6Address"

        return cls.default_ipv6_gateway




if __name__ in "__main__":

    print(f"Before instantiating IPv4Route, the default gateway is {IPv4Route.get_default_ipv4_gateway()}")
    ipv4_route_lst = IPv4Route.find_ipv4_routes()
    print(40*"=")
    for r in ipv4_route_lst:
        print(r.__str__() )
        print(f"The gateway is {r.ipv4_gateway}\n")
    # Commercialventvac.com's canonical name
    COMMERCIALVENTVAC = "ps558161.dreamhost.com"
    COMMERCIALVENTVAC_ADDR = "208.97.189.29"
    """
>>> socket.inet_pton(socket.AF_INET,"208.97.189.29")
b'\xd0a\xbd\x1d'
>>> 
    """
    COMMERCIALVENTVAC_BYTES = b'\xd0a\xbd\x1d'
    cvv_ip_v4 = IPv4Address(name=COMMERCIALVENTVAC)
    assert str(cvv_ip_v4) == COMMERCIALVENTVAC or str(cvv_ip_v4) == COMMERCIALVENTVAC_ADDR,\
        f"commercialventvac by name should be {COMMERCIALVENTVAC} but is actually {str(cvv_ip_v4)}"
    cvv_ip_v4_by_addr = IPv4Address(ipv4_address=COMMERCIALVENTVAC_ADDR)
    assert str(cvv_ip_v4_by_addr) == COMMERCIALVENTVAC or \
           str(cvv_ip_v4_by_addr) == COMMERCIALVENTVAC_ADDR, \
        f"commercialventvac by addr should be {COMMERCIALVENTVAC} but is actually {str(cvv_ip_v4)}"
    assert cvv_ip_v4.ipv4_address == COMMERCIALVENTVAC_BYTES, \
        f"cvv_ip_v4.ipv4_address should be b'\xd0a\xbd\x1d' but is actually "\
        f"{cvv_ip_v4.ipv4_address}"
    assert cvv_ip_v4_by_addr.ipv4_address == COMMERCIALVENTVAC_BYTES, \
        f"cvv_ip_v4_by_addr.ipv4_address should be b'\xd0a\xbd\x1d' but is actually "\
        f"{cvv_ip_v4_by_addr.ipv4_address}"

    cprint("Running ping tests, plz be patient"
           "", "green", file=sys.stderr )
    up, slow = cvv_ip_v4_by_addr.ping4()
    if up : cprint(f"{cvv_ip_v4_by_addr.name} is  pingable", 'green')
    else: cprint(f"{cvv_ip_v4_by_addr.name} is NOT pingable", "red")

    production = False          # Do NOT raise the exception
    answer = IPv4Address(name='192.168.0.143').ping4(production=production)
    assert not answer[0] , f"192.168.0.143 is pingable and it should NOT be. " \
                        f" Answer is {answer} "
    try:
        production = True
        answer = IPv4Address(name='192.168.0.143').ping4(production=production)
        assert not answer[0], f"192.168.0.143 is pingable and it should NOT be.  " \
                           f"Answer is {answer} "
    except NotPingable as n:
        cprint(f"Handling the NotPingable exception on 192.168.0.143 production is {production} answer is {answer}", 'white', 'on_red', file=sys.stderr)

    assert IPv4Address(name='google.com').ping4(production=False)[0], "google.com is not pingable and it should be"
    try:
        answer = IPv4Address(name='spurious.spurious').ping4(production=False)[0]
    except ( DNSFailure)  as d:
        cprint("Detected a DNSFailure as expected", "green", file=sys.stderr )
    except socket.gaierror as s:
        cprint("Detected a socket.gaierror as expected", "green", file=sys.stderr)
    else:
        cprint("Did NOT Detect a DNSFailure or socket.gaierror.  This is an error", "red", file=sys.stderr)





    # This is mentioned in Issue 5
    cprint("IPv6 tests not implemented yet", "magenta", "on_yellow")











