#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This module is responsible for representing the routing tables.  There are at least 2: one for IPv4 and one for IPv6
import socket
import subprocess
import sys

IP_COMMAND="/sbin/ip"

class DNSFailure(Exception):
    pass


class IPv4_address(object):
    """
    This object has an IPv4 object.  It has two attributes: name and ipv4_address.
    If the name has not been specified, then it is None
    """

    def __init__(self, name : str =None, ipv4_address : [str, bytes] = None):
        if name is not None:
            self.name = name
            if ipv4_address is None:
                # This may raise a socket.gaierror error if gethostbyname fails.  The error will propogate back to the caller
                ipv4_address = socket.gethostbyname(name)
        if ipv4_address is not None:
            if isinstance(ipv4_address, str):
                # https://docs.python.org/3/library/socket.html#socket.inet_pton
                self.ipv4_address = socket.inet_pton(socket.AF_INET, ipv4_address)
            elif isinstance(ipv4_address, bytes) and len(ipv4_address) == 4 :
                self.ipv4_address = ipv4_address
            else:
                raise ValueError(f"ipv4_address is of type {type(ipv4_address)}"\
                                 "should be bytes or str")


    def __str__(self):
        # https://docs.python.org/3/library/socket.html#socket.inet_ntop
        ipv4_addr_str = socket.inet_ntop(socket.AF_INET, self.ipv4_address)
        return ipv4_addr_str

    def ping(self, count=4, max_allowed_delay=1000):
        """Verifies that an IPv4 address is pingable.
        :param  count   How many times to ping the IP address
        :param  max_allowed_delay


        :returns False if the remote device is unpingable

        A future version will return a tuple with the package loss percentage, statistics about delay, etc.
        """

        completed = subprocess.run(['ping', self.ipv4_address])
        # return status = 0 if everything is okay
        # return status = 2 if DNS fails to look up the name
        # return status = 1 if the device is not pingable
        if completed.returncode == 2:
            raise DNSFailure
        return completed.returncode == True




class IPv6_address(object):
    def __init__(self, name : str = None, ipv6_address : [str, ] = None ):
        if name is not None:
            self.name = name
        # Needs work
        self.ipv6_address = ipv6_address



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

    def __init__(self, route ):
        """This returns an IPv4Route object.  """

 # Use caution: these are strings, not length 4 bytes
        self.ipv4_destination = route['ipv4_destination']  # Destination must be present
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
                    name = socket.gethostbyaddr(destination)
                except socket.herror as h:
                    # This exception will happen, because the IPv4 addresses in the LAN are probably not in DNS or in
                    # /etc/hosts.  Now, should I print the message, even though I expect it?
                    # says that it can so I have to handle it
                    print("socket.gethostbyaddr raised a socket.herror "
                          "exception on %s, continuing" % destination, str(h), file=sys.stderr )
                except socket.gaierror as g:
                    print("socket.gethostbyaddr raised a socket.gaierror "
                          "exception on %s, continuing" % destination, str(g),
                          file=sys.stderr )
                else:
                    pass
                name = destination
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
        for line in lines:      # lines is the output of the ip route list
            # command
            fields = line.split()
            destination = translate_destination(fields[0])

            route=dict()
            route['ipv4_destination'] = destination
            for i in range(1, len(fields), 2):
                if fields[i] == 'linkdown':
                    route['linkdown'] = True
                    break
                route[fields[i]] = fields[i+1]
            ipv4_route = IPv4Route( route=route )
            if destination == "default" or destination == "0.0.0.0":
                cls.default_gateway = ipv4_route
            route_list.append(ipv4_route)
            """
            route_list.append(self.IPv4_route(name=name,
                                              ipv4_destination=ipv4_destination,
                                              ipv4_gateway=ipv4_gateway,
                                              ipv4_mask=ipv4_mask,
                                              ipv4_flags=ipv4_flags,
                                              ipv4_metric=ipv4_metric,
                                              ipv4_ref=ipv4_ref,
                                              ipv4_use=ipv4_use,
                                              ipv4_interface=ipv4_interface))
            """
        return route_list

    def __str__(self):
        """This method produces a nice string representation of a IPv4_route object"""
        return f"dest={self.ipv4_destination} gateway={self.ipv4_gateway} " \
               f"dev={self.ipv4_dev} " \
               f"metric={self.ipv4_metric} proto={self.ipv4_proto} "\
               f"src={self.ip4v_src} scope={self.ipv4_scope} " + \
               ( "linkdown" if self.ipv4_linkdown else "linkUP" )

    @classmethod
    def get_default_gateway(cls):
        """Returns the default gateway.  If the default gateway attribute does not exist, then this method ought to
        invoke find_ipv4_routes, which will define the default gateway"""
        if not hasattr(cls, "default_gateway"):
            # This has some overhead, and ought to be cached somehow.  Deal with that later.
            cls.find_ipv4_routes()
        return cls.default_gateway


class IPv6Route(object):
    def __init__(self, name, ipv6_destination, ipv6_next_hop, ipv6_flags, ipv6_metric, ipv6_ref, ipv6_use, \
                 ipv6_interface):
        self.name = name
        self.ipv6_destination = ipv6_destination
        self.ipv6_next_hop = ipv6_next_hop
        self.ipv6_flags = ipv6_flags
        self.ipv6_metric = ipv6_metric
        self.ipv6_ref = ipv6_ref
        self.ipv6_use = ipv6_use
        self.ipv6_interface = ipv6_interface

    @classmethod
    def find_all_ipv6_routes(cls):
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
                                   stdout=None, stderr=None, shell=False, timeout=None, check=False, encoding=None,
                                   errors=None)
        route_list = []
        for r in completed:
            (ipv6_destination, _dev_, ipv6_interface,) = r.split()


if __name__ in "__main__":
    print(f"Before instantiating IPv4Route, the default gateway is {IPv4Route.get_default_gateway()}")
    ipv4_route_lst = IPv4Route.find_ipv4_routes()
    print(f"The default gateway is {IPv4Route.default_gateway}")
    print(40*"=")
    for r in ipv4_route_lst:
        print(r.__str__() )
        print(f"The gateway is {r.ipv4_gateway}\n")


