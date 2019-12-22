#!

# This file has utility functions that will be generally useful


import json
import platform
import subprocess
import sys
from enum import Enum
from typing import List
import termcolor

from constants import ErrorLevels, colors

"""
>>> platform.system()
'Linux'
>>> 
>>> platform.linux_distribution()
('Ubuntu', '18.04', 'bionic')
>>> platform.dist()
('Ubuntu', '18.04', 'bionic')
>>> 

>>> platform.mac_ver()
('', ('', '', ''), '')
>>> 
>>> platform.win32_ver()
('', '', '', '')
>>> 
>>> platform.mac_ver()
('', ('', '', ''), '')
>>> 


"""


class OSILevels(Enum):
    PHYSICAL = 1
    MEDIAACCESSCONTROL = 2
    NETWORK = 3
    TRANSPORT = 4
    SESSION = 5
    PRESENTATION = 6
    APPLICATION = 7


class SystemConfigurationFile(object):
    """This class handles interfacing between the program and the configuration file.  Thus, when the system is in its
    'nominal' state, then that's a good time to write the configuration file.  When the state of the system is
    questionable, then that's a good time to read the configuration file"""

    def __init__(self, filename):
        """Create a SystemConfigurationFile object which has all of the information in a system configuration file"""

        with open(filename, "r") as json_fp:
            self.system_description = json.load(json_fp)

    def save_state(self, filename):
        with open(filename, "w") as json_fp:
            json.dump(self, json_fp, ensure_ascii=False)

    def compare_state(self, the_other):
        """This method compares the 'nominal' state, which is in self, with another state, 'the_other'.  The output is
    a dictionary which is keyed by field.  The values of the dictionary are a dictionary with three keys:
    Comparison.NOMINAL, Comparison.OTHER.  The values of these dictonaries will be objects
    appropriate for what is being compared.  If something is not in Comparison.NOMINAL and not in Comparison.DIFFERENT,
     then there is no change.  
    
        """
        pass


class OsCliInter(object):
    """
    A collection of methods for running CLI commands.
    """

    # Since the system is going to be the same across the entire program, populate it when the OsCliInter object is
    # imported for the first time and then make it available to any object in class OsCliInter (which should not need
    # to be instantiated
    system = platform.system()

    @classmethod
    def run_command(cls, command: List[str]) -> str:
        """
        Run the command on the CLI

        :param command: a list of strings.  Element 0 is the name of the executable. The rest of the list are args to
        the command
        :return: A string which is the output of the program in ASCII
        """

        completed: subprocess.CompletedProcess = subprocess.run(command,
                                                                stdin=None,
                                                                input=None,
                                                                stdout=subprocess.PIPE, stderr=None, shell=False,
                                                                timeout=None,
                                                                check=False)
        completed_str = completed.stdout.decode('ascii')
        return completed_str


# DNS sits at the application layer in the OSI model, according to
# https://en.wikipedia.org/wiki/List_of_network_protocols_(OSI_model)
# But since DNS is useful at many different levels in the stack, I am moving
# the DNSFailure exception class from here to utilities.py
# https://github.com/jeffsilverm/nbmdt/issues/40

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

        report(condition=f"DNSFailure was raised querying {name} using query type "
               f"{query_type}", severity=ErrorLevels.OTHER)
        Exception.__init__(self, *args)


def report(condition: str, severity: ErrorLevels) -> None:
    """
    Report all problems here.  Eventually, report will include a logging
    capability.

    :param condition: A string that describes the problem
    :param severity: An enum that shows how severe the problem is
    :return: None
    """

    termcolor.cprint(condition, color=colors[severity][0], on_color=colors[severity][1], file=sys.stderr)


if "__main__" == __name__:
    import dns.resolver

    from constants import ErrorLevels as ELs

    for e in ELs:
        report(f"ErrorLevel {e.name}", severity=e)

    report("All's well", severity=ErrorLevels.NORMAL)

    # Issue 40 https://github.com/jeffsilverm/nbmdt/issues/40
    # The method query_specific_nameserver was here, now moved to utilities.py
    def query_specific_nameserver(server_list: list, qname: str, rdatatype: str):
        """

        :param server_list: A list of servers (possibly length 1) to query
        :param qname:   The thing to query for
        :param rdatatype:   The kind of queries to make
        :return: A list of answers
        """
        # I'm getting bogged down in details.  As of this writing (2019/11/17),
        # I just want to be able to do a DNS query!
        # dns.resolver.default_resolver.nameservers = server_list
        assert len(server_list) >= 1
        answer: dns.resolver.Answer = dns.resolver.query(qname=qname, rdatatype=rdatatype)
        # answer.sort()
        return answer


    # This is here as part of issue 40
    # https://github.com/jeffsilverm/nbmdt/issues/40
    def resolver_tst(tst_resolver, qname="google.com", rdatatype=dns.rdatatype.A):
        """
        :param  tst_resolver    str:    the resolver to test
        :param  qname   str:    the string to do the query on (usually the remote server)
        :param rdatatype: dns.rdatatype The data type to query, A, AAAA, MX, PTR, etc.
        """
        answer = query_specific_nameserver(server_list=tst_resolver,
                                           qname="commercialventvac.com",
                                           rdatatype=dns.rdatatype.A)
        ns_okay = True
        for rr in answer:
            print(f"  {rr}")
            if rr is not None and rr not in ["208.97.189.29"]:
                report(
                    f"server {resolver} returned unanticipated IPv4 answer {rr}",
                    ErrorLevels.OTHER)
                ns_okay = False
        answer = query_specific_nameserver(server_list=tst_resolver,
                                           qname="commercialventvac.com",
                                           rdatatype=dns.rdatatype.AAAA)
        for rr in answer:
            print(f"  {rr}")
            if rr is not None and rr not in ["2607:f298:5:115f::23:e397"]:
                report(
                    f"server {resolver} returned unanticipated IPv6 answer {rr}",
                    ErrorLevels.OTHER)
                ns_okay = False
        return ns_okay


    report(f"Testing local DNS resolvers from /etc/resolv.conf", ErrorLevels.NORMAL)
    resolver_obj = dns.resolver.Resolver()

    print(resolver_obj.nameservers)
    failed_resolver_list = []
    all_okay = True  # Assume everything is fine until we find something that is NOT fine
    for resolver in resolver_obj.nameservers + ['8.8.8.8']:
        print(40 * '=' + '\n' + f"Working on resolver {resolver}")
        okay = resolver_tst(tst_resolver=resolver, rdatatype=dns.rdatatype.A)
        if not okay:
            failed_resolver_list.append(resolver)
            report(f"Resolver {resolver} failed the IPv4 test.", ErrorLevels.DOWN)
        all_okay = all_okay and okay
        okay = resolver_tst(tst_resolver=resolver, rdatatype=dns.rdatatype.AAAA)
        if not okay:
            failed_resolver_list.append(resolver)
            report(f"Resolver {resolver} failed the IPv6 test.", severity=ErrorLevels.DOWN)
        all_okay = all_okay and okay
    if len(failed_resolver_list) == 0:
        report("All resolvers pass IPv4 checks", severity=ErrorLevels.NORMAL)
    else:
        report(f"Some resolvers failed.  They are:{failed_resolver_list}", severity=ErrorLevels.DOWN)

#    report(f"Testing a non-existant resolver", severity=ErrorLevels.OTHER)
#    okay = resolver_tst(resolver=['192.168.0.143'], qname="google.com", rdatatype=dns.rdatatype.A)
