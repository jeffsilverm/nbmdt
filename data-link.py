#! /usr/bin/python3

from interfaces import none_if_none, PhysicalInterface
import sys
import subprocess
from configuration import IP_COMMAND
import collections


class LogicalInterface(object):
    """Logical links have IPv4 and IPv6 addresses associated with them as known by the ip addr list command

    """

    logical_link_db = dict()

    # Re-write this as PhysicalInterface does it, with the addr_name as a field and then a description which is a
    # dictionary.
    def __init__(self, addr_name_, addr_family, addr_addr, addr_descr,
                 scope=None, broadcast=None, remainder=None):
        """This creates a logical interface object.
        :param  addr_name_   The name, as gethostbyaddr returns or what you feed to gethostbyname, or None
        :param  addr_family "inet" or "inet6"
        :param  addr_addr   The IPv4 address if addr_family is "inet" or the IPv6 address if addr_family is "inet6"
        :param  addr_descr  ?
        :param  scope       ?
        :param
        """
        if addr_family != "inet" and addr_family != "inet6":
            raise ValueError(
                "misunderstood value of addr_family: {}".format(addr_family))
        self.addr_name = addr_name_
        self.addr_family = addr_family
        self.addr_addr = addr_addr
        self.addr_descr = addr_descr
        # I have to have a better understanding of the symantecs of scope and
        # broadcast
        if ((scope is None) + (broadcast is None)) != 1:  # True + True =
            #  2, True + False == False + True == 1, False + False == 0
            print(
                "While instantiating {}, ".format(addr_name_),
                "One and only one of scope or broadcast must be None\n" 
                "scope is {} broadcast is {}\n".format(str(scope),
                                                       str(broadcast)),
                file=sys.stderr)
        self.scope = scope
        self.broadcast = broadcast
        self.remainder = remainder

    def __str__(self):
        s = "name: " + self.addr_name + '\t'
        s += "family:" + self.addr_family + '\t'
        s += "address: " + self.addr_addr + '\t'
        if self.addr_family == "inet6":
            s += ("scope: " + none_if_none(self.scope) + "\t")
        else:
            s += ("broadcast: " + none_if_none(self.broadcast) + "\t")
        s += "Remainder: " + none_if_none(self.remainder) + "\t"
        return s

    @classmethod
    def get_all_logical_link_addrs(cls):
        """This method creates a dictionary, keyed by name, of all of the (logical) links that have addresses.
        Since an interface can, and probably will, have more than one address, the values of this dictionary
        will be dictionaries keyed by address which will contain a description of the address"""

        completed = subprocess.run(
            [IP_COMMAND, "--details", "--oneline", "addr", "list"], stdin=None,
            input=None,
            stdout=subprocess.PIPE, stderr=None, shell=False, timeout=None,
            check=False)
        completed_str = completed.stdout.decode('ascii')
        addrs_list = completed_str.split('\n')
        for line in addrs_list:
            """
jeffs@jeffs-laptop:~/nbmdt (development)*$ /usr/sbin/ip --oneline --detail 
addr show
1: lo    inet 127.0.0.1/8 scope host lo\       valid_lft forever preferred_lft forever
1: lo    inet6 ::1/128 scope host \       valid_lft forever preferred_lft forever
3: wlp12s0    inet 10.1.10.146/24 brd 10.1.10.255 scope global dynamic wlp12s0\       valid_lft 597756sec 
preferred_lft 597756sec
3: wlp12s0    inet6 fc00::1:2/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 2618::1/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 ff::1/128 scope global \       valid_lft forever preferred_lft forever
3: wlp12s0    inet6 fe80::5839:4589:a697:f8fd/64 scope link \       valid_lft forever preferred_lft forever
4: virbr0    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0\       valid_lft forever preferred_lft 
forever
jeffs@jeffs-laptop:~/nbmdt (development)*$

            """
            # if family is inet, then brd_scope is brd (broadcast) and brd_scope_val is the the broadcast IPv4 address
            # if family is inet6, then brd_scope is scope\ and brd_scope_val is either host, link, or global
            try:
                idx, link_name, family, addr_mask, brd_scope, brd_scope_val, remainder = line.split()[0:7]
            except ValueError as v:
                print(
                    f"Raised ValueError.  Error is {str(v)}.  line is \n{line}\nTrying again ",
                    file=sys.stderr)
                fields = line.split()
                print(f"There are actually {len(fields)} in line",
                      file=sys.stderr)
                idx, link_name, family, addr_mask, brd_scope, brd_scope_val = fields[0:7]

            """                                                                 
            logical_link_descr = cls.__init__(addr_name=link_name,
                                              addr_family=family,
                                              addr_addr=addr_mask,
                                              scope=(
                                                  brd_scope if family == "inet" else None),
                                              broadcast=(
                                                  None if family == "inet" else brd_scope),
                                              )
            """

            print("kludged the logical link DB in interfaces.py")
            cls.logical_link_db[link_name] = line.split()[0:7]

    @classmethod
    def get_all_logical_interfaces(cls):
        """This method returns a dictionary, keyed by name, of logical interfaces as known by the ip address list
        command.  Note that if a physical link does not an IPv4 address or an IPv6 address, then the ip command doesn't
        show it.  If a physical link has an IPv4 address and an IPv6 address, then there will be 2 entries"""

        completed = subprocess.run([IP_COMMAND, "--oneline", "address", "list"],
                                   stdin=None, input=None,
                                   stdout=subprocess.PIPE, stderr=None,
                                   shell=False, timeout=None, check=False)
        completed_str = completed.stdout.decode('ascii')
        # addrs_list is really a list of logical interfaces
        addrs_list = completed_str.split('\n')
        addr_dict = dict()
        for addr_ in addrs_list:
            # addrs_list usually but not always has an empty element at the end
            if len(addr_) == 0:
                break
            # https://docs.python.org/3/library/collections.html#collections.OrderedDict
            # ad is an attribute dictionary.  The string returned by the ip command will look like:
            # 3: wlp12s0    inet 10.5.66.10/20 brd 10.5.79.255 scope global dynamic wlp12s0\       valid_lft 85452sec
            #  preferred_lft 85452sec
            ad = collections.OrderedDict()
            fields = addr_.split()
            addr__name = fields[1]

            addr_family = fields[2]  # Either inet or inet6
            assert addr_family == "inet" or addr_family == "inet6"
            addr_addr = fields[3]
            for idx in range(4, len(fields) - 1, 2):
                # Because ad is an ordered dictionary, the results will always be output in the same order
                ad[fields[idx]] = fields[idx + 1]
            # A single logical interface can have several addresses and several families
            # so the logical interface name is a key to a value which is a list
            # of addresses.
            if addr__name not in addr_dict:
                # addr__name, addr_family, addr_addr, scope=None, broadcast=None, remainder=None
                addr_dict[addr__name] = [LogicalInterface(addr_name_=addr__name,
                                                          addr_family=addr_family,
                                                          addr_addr=addr_addr,
                                                          addr_descr=ad)]
            else:
                addr_dict[addr__name].append(LogicalInterface(addr_name_=addr__name,
                                                              addr_family=addr_family,
                                                              addr_addr=addr_addr,
                                                              addr_descr=ad))
        return addr_dict


if __name__ == "__main__":
    # nominal = SystemDescription.describe_current_state()

    # Create a list of all the physical interfaces
    link_db = PhysicalInterface.get_all_physical_interfaces()
    # Create a dictionary, keyed by link name, of the logical interfaces, that is, interfaces with addresses
    addr_db = LogicalInterface.get_all_logical_interfaces()

    print("links ", '*' * 40)
    for link in link_db:
        print(link, ":||  ", end=" ")
        properties: dict = PhysicalInterface.link_properties(ifname=link)
        for prop in properties:
            if len(properties[prop]) == 1:
                print(prop, ": ", properties[prop][0], end=" ")
            else:  # It is a list of values, so print the entire list.
                print(prop, ": ", properties[prop], end=" ")

        if len(link) == 10000:  # To fool pycharm
            mac_addr = properties['address']
            print(link, mac_addr, properties['state'])
        print(end="\n")
    print("Addresses ", '*' * 40)
    for addr_name in addr_db:
        print("\n{}\n".format(addr_name))
        for addr in addr_db[addr_name]:  # The values of the addr_db are descriptions of addresses
            assert isinstance(addr, LogicalInterface)
            print("   " + str(addr))
