#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import re
import datetime
import collections

IP_COMMAND = "/usr/sbin/ip"
# There is an ip command cheat sheet at https://access.redhat.com/sites/default/files/attachments/rh_ip_command_cheatsheet_1214_jcs_print.pdf

def none_if_None ( s ):
    return s if s is not None else "None"


class PhysicalInterface ( object ):


    def __init__  ( self, intf_name, intf_description ):
        self.intf_name = intf_name
        self.intf_description = intf_description.copy()

    def __str__(self):
        s = "name: " + self.intf_name
        for key in self.intf_description.keys() :
            s += "\t" + key + ": " + self.intf_description[key]

        return s



    @classmethod
    def get_all_physical_interfaces(self):
        """This method returns a dictionary of interfaces as known by the ip link list command
        """

        completed = subprocess.run([IP_COMMAND, "--details", "--oneline", "link", "list"], stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        links_list = completed_str.split('\n')
        link_db = dict()
        for link in links_list:
            if len(link) == 0:              # there may be an empty trailing line in the output
                break
            fields = link.split()
            intf_description = collections.OrderedDict()
            intf_name = fields[1][:-1]  # strip off the trailing colon, so for example, eno1: becomes eno1
            intf_description['flags'] = fields[2]
            # Issue 1 https://github.com/jeffsilverm/nbmdt/issues/1
            for idx in range(3,len(fields)-1,2)  :
                # Accortding to http://lartc.org/howto/lartc.iproute2.explore.html , qdisc stands for "Queueing
                # Discipline" and it's vital.
                intf_description[fields[idx]] = fields[idx+1]
            link_db[ intf_name ] = PhysicalInterface( intf_name, intf_description )

        return link_db

# There should be a class method here that contains a dictionary of all of the PhysicalInterfaces


class LogicalInterface ( object ) :
    """Logical links have IPv4 and IPv6 addresses associated with them as known by the ip addr list command

    """

    logical_link_db = dict()

    # Re-write this as PhysicalInterface does it, with the addr_name as a field and then a description which is a
    # dictionary.
    def __init__(self, addr_name, addr_family, addr_addr, scope=None, broadcast=None, remainder=None   ) :
        """This creates a logical interface object."""
        if addr_family != "inet" and addr_family != "inet6" :
            raise ValueError ("misunderstood value of addr_family: {}".format( addr_family ))
        self.addr_name=addr_name
        self.addr_family=addr_family
        self.addr_addr=addr_addr
        if ( scope is None + broadcast is None ) != 1:      # True + True = 2, True + False == False + True == 1, False + False == 0
            raise ValueError ("One and only one of scope or broadcast must  be None")
        self.scope=scope
        self.broadcast=broadcast
        self.remainder=remainder



    def __str__(self):
        s = "name: " + self.addr_name + '\t'
        s += "family:" + self.addr_family + '\t'
        s += "address: " + self.addr_addr + '\t'
        if self.addr_family == "inet6" :
            s += ("scope: " + none_if_None(self.scope) + "\t")
        else :
            s += ("broadcast: " + none_if_None ( self.broadcast ) + "\t" )
        s += "Remainder: " + none_if_None ( self.remainder  ) + "\t"
        return s

    @classmethod
    def get_all_logical_link_addrs(cls):
        """This method creates a dictionary, keyed by name, of all of the (logical) links that have addresses.
        Since an interface can, and probably will, have more than one address, the values of this dictionary
        will be dictionaries keyed by address which will contain a description of the address"""


        completed = subprocess.run([IP_COMMAND, "--details", "--oneline", "addr", "list"], stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        addrs_list = completed_str.split('\n')
        for line in addrs_list:
            """
effs@jeffs-laptop:~/nbmdt (development)*$ /usr/sbin/ip --oneline --detail addr show
1: lo    inet 127.0.0.1/8 scope host lo\       valid_lft forever preferred_lft forever
1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever
3: wlp12s0    inet 10.1.10.146/24 brd 10.1.10.255 scope global dynamic wlp12s0\       valid_lft 597756sec preferred_lft 597756sec
3: wlp12s0    inet6 fc00::1:2/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 2618::1/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 ff::1/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 fe80::5839:4589:a697:f8fd/64 scope link \       valid_lft forever preferred_lft forever
4: virbr0    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0\       valid_lft forever preferred_lft forever
jeffs@jeffs-laptop:~/nbmdt (development)*$

            """
            # if family is inet, then brd_scope is brd (broadcast) and brd_scope_val is the the broadcast IPv4 address
            # if family is inet6, then brd_scope is scope\ and brd_scope_val is either host, link, or global
            idx, link_name, family, addr_mask, brd_scope, brd_scope_val,remainder = line.split()
            logical_link_descr =  cls.__init__(addr_name=link_name, addr_family=family, addr_addr=addr_mask,
                                               scope = ( brd_scope if family == "inet" else None),
                                               broadcast = ( None if family == "inet" else brd_scope),
                                               )
            cls.logical_link_db[link_name] = logical_link_descr




    @classmethod
    def get_all_logical_interfaces(self):
        """This method returns a dictionary, keyed by name, of logical interfaces as known by the ip address list
        command.  Note that if a physical link does not an IPv4 address or an IPv6 address, then the ip command doesn't
        show it.  If a physical link has an IPv4 address and an IPv6 address, then there will be 2 entries"""

        completed = subprocess.run([IP_COMMAND, "--oneline", "address", "list"], stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        # addrs_list is really a list of logical interfaces
        addrs_list = completed_str.split('\n')
        addr_db = dict()
        for addr in addrs_list :
            # addrs_list usually but not always has an empty element at the end
            if len(addr) == 0:
                break
            # https://docs.python.org/3/library/collections.html#collections.OrderedDict
            # ad is an attribute dictionary.  The string returned by the ip command will look like:
            # 3: wlp12s0    inet 10.5.66.10/20 brd 10.5.79.255 scope global dynamic wlp12s0\       valid_lft 85452sec preferred_lft 85452sec
            ad = collections.OrderedDict()
            fields = addr.split()
            addr_name = fields[1]

            addr_family = fields[2] # Either inet or inet6
            assert addr_family == "inet" or addr_family == "inet6"
            addr_addr = fields[3]
            for idx in range(4,len(fields)-1, 2) :
                # Because ad is an ordered dictionary, the results will always be output in the same order
                ad[fields[idx] ] = fields[idx+1]
            # A single logical interface can have several addresses and several families
            if addr_name not in addr_db:
                # addr_name, addr_family, addr_addr, scope=None, broadcast=None, remainder=None
                addr_db[addr_name] = [  LogicalInterface ( addr_name=addr_name, addr_family=addr_family, addr_addr=addr_addr, ad=ad  ) ]
            else :
                addr_db[addr_name].append( LogicalInterface ( addr_name=addr_name, addr_family=addr_family, addr_addr=addr_addr, ad=ad  ) )
        return addr_db


if __name__ == "__main__":
    # nominal = SystemDescription.describe_current_state()

    # Create a dictionary, keyed by link name, of the physical interfaces
    link_db = PhysicalInterface.get_all_physical_interfaces()
    # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
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
