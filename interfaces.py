#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import datetime
import collections


class PhysicalInterface ( object ):


    def __init__  ( self, name, link_description ):
        self.link_name = name
        self.link_description = link_description.copy()

    def __str__(self):
        s = "name: " + self.link_name
        for key in self.link_description.keys() :
            s += "\t" + key + ": " + self.link_description[key]

        return s



    @classmethod
    def get_all_physical_interfaces(self):
        """This method returns a dictionary of interfaces as known by the ip link list command
        """

        completed = subprocess.run(["/bin/ip", "--details", "--oneline", "link", "list"], stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        links_list = completed_str.split('\n')
        link_db = dict()
        for link in links_list:
            if len(link) == 0:              # there may be an empty trailing line in the output
                break
            fields = link.split()
            link_description = collections.OrderedDict()
            link_name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
            link_description['flags'] = fields[2]
            # Issue 1 https://github.com/jeffsilverm/nbmdt/issues/1
            for idx in range(3,len(fields)-1,2)  :
                # Accortding to http://lartc.org/howto/lartc.iproute2.explore.html , qdisc stands for "Queueing
                # Discipline" and it's vital.
                link_description[fields[idx]] = fields[idx+1]
            link_db[ link_name ] = PhysicalInterface( link_name, link_description )

        return link_db

# There should be a class method here that contains a dictionary of all of the PhysicalInterfaces


class LogicalInterface ( object ) :

    def __init__(self, addr_name, addr_family, addr_addr, ad  ) :
        """This creates a logical interface object."""
        if addr_family != "inet" and addr_family != "inet6" :
            raise ValueError ("misunderstood value of addr_family: {}".format( addr_family ))
        self.addr_name=addr_name
        self.addr_family=addr_family
        self.addr_addr=addr_addr
        self.ad = ad                # ad is going to go out of existence, but the reference to it will endure


    def __str__(self):
        s = " name: " + self.addr_name + '\n'
        s += " family:" + self.addr_family
        s += " address: " + self.addr_addr
        for key in self.ad.keys() :
            s += "\t" + key + ": " + self.ad[key]
        return s




# There should be a class method here that contains a dictionary of all of the LogicalInterfaces




    @classmethod
    def get_all_logical_interfaces(self):
        """This method returns a dictionary of logical interfaces as known by the ip address list command"""

        completed = subprocess.run(["/bin/ip", "--oneline", "address", "list"], stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        addrs_list = completed_str.split('\n')
        addr_db = dict()
        for addr in addrs_list :
            if len(addr) == 0:
                break
            # https://docs.python.org/3/library/collections.html#collections.OrderedDict
            ad = collections.OrderedDict()
            fields = addr.split()
            addr_name = fields[1]

            addr_family = fields[2]
            addr_addr = fields[3]
            for idx in range(4,len(fields)-1, 2) :
                # Because ad is an ordered dictionary, the results will always be output in the same order
                ad[fields[idx] ] = fields[idx+1]
            # A single logical interface can have several addresses and several families
            if addr_name not in addr_db:
                addr_db[addr_name] = [  LogicalInterface ( addr_name, addr_family, addr_addr, ad  ) ]
            else :
                addr_db[addr_name].append( LogicalInterface ( addr_name, addr_family, addr_addr, ad  ) )
        return addr_db


if __name__ == "__main__":
    # nominal = SystemDescription.describe_current_state()

    # Create a dictionary, keyed by link name, of the physical interfaces
    link_db = PhysicalInterface.get_all_physical_interfaces()
    addr_db = LogicalInterface.get_all_logical_interfaces()

    print("links ", '*'*40)
    for link in link_db.keys() :
        print ( link, link_db[link] )

    print("Addresses ", '*'*40)
    for addr_name in addr_db.keys() :
        print("\n{}\n".format(addr_name) )
        for addr in addr_db[addr_name] :      # The values of the addr_db are descriptions of addresses
            assert isinstance( addr, LogicalInterface )
            print("   " + str(addr)  )
