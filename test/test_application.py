#! /usr/bin/python3

import application
from termcolor import cprint as cprint
import sys

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
QNAME = "google.com"


def resolver_test(my_dns, resolver, qname, rdatatype: dns.rdatatype = dns.rdatatype.A):
    # server_list: list, qname: str, rdatatype: dns.

    answer:List[str] = my_dns.query_specific_nameserver(qname, server_list=resolver,  rdatatype=rdatatype)
    for rr in answer:
        print(f"  {rr}")


    okay = True
    answer = my_dns.query_specific_nameserver(server_list=[resolver],
                                           qname=QNAME,
                                           rdatatype=dns.rdatatype.AAAA)
    for rr in answer:
        print(f"  {rr}")
        # Do not hard hard coded name servers here, see Issue 18
        # https://github.com/jeffsilverm/nbmdt/issues/18
        if rr not in ["2607:f8b0:4008:80d::200e", '2607:f8b0:4004:811::200e']:
            cprint(
                f"server {resolver} returned unanticipated IPv6 answer rr",
                'yellow')
            okay = False
    return okay


my_dns = application.DNS()
cprint("Get list of DNS resolvers, perhaps from /etc/resolv.conf", "blue", file=sys.stderr)
local_resolvers = my_dns.get_resolvers()
cprint(local_resolvers, "blue", file=sys.stderr)
failed_resolver_list = []
all_okay = True
# In addition to any local resolvers, test some well know public resolvers
for resolver in local_resolvers + ['8.8.8.8', '8.8.4.4', '2001:4860:4860::8888', '2001:4860:4860::8844']:
    cprint(40 * '=' + '\n' + f"Working on resolver {resolver}", 'blue')
    okay = resolver_test(my_dns, resolver=resolver, qname=QNAME, rdatatype=rdatatype.A)
    # Issue 19 https://github.com/jeffsilverm/nbmdt/issues/19
    if not okay:
        failed_resolver_list.append(resolver)
        cprint(f"Resolver {resolver} failed the IPv4 test.", 'red')
    all_okay = all_okay and okay
    okay = resolver_test(my_dns, resolver=resolver, qname=QNAME, rdatatype=rdatatype.AAAA)
    # Issue 19 https://github.com/jeffsilverm/nbmdt/issues/19
    if not okay:
        failed_resolver_list.append(resolver)
        cprint(f"Resolver {resolver} failed the IPv6 test.", 'red')
    all_okay = all_okay and okay
if len(failed_resolver_list) == 0:
    cprint("All resolvers pass IPv4 checks", 'green')
else:
    cprint(f"Some resolvers failed.  They are:{failed_resolver_list}", 'red')
    # Issue 19 https://github.com/jeffsilverm/nbmdt/issues/19
cprint(f"Testing a non-existant resolver", 'blue', file=sys.stderr)
# Issue 18 does *not* apply here because this is testing for a non-existant router
# Issue 19 https://github.com/jeffsilverm/nbmdt/issues/19
okay = resolver_test(resolver=['192.168.0.143'], qname="google.com", rdatatype=rdatatype.A)
