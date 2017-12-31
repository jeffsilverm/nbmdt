#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Contains a class for applications and a class for DNS, which is an application

from termcolor import cprint
import sys

class Applications(object):
    pass

# DNS sits at the application layer in the OSI model, according to
# https://en.wikipedia.org/wiki/List_of_network_protocols_(OSI_model)
class DNSFailure(Exception):

    # Eventually, I'd like a DNSFailure exception to include the name being looked
    # up and the kind of query being made.
    # Issue 12
    def __init__(self, name : str = None, query_type : str = 'A', *args, **kwargs ) -> None:
        '''
        :param name: str  The subject of the query
        :param query_type: str  The type of query.  Default is 'A', an IPv4 name query
        :param args:
        :param kwargs:
        '''
        def __init__(self, ):
            cprint (f"DNSFailure was raised querying {name} using query type {query_type}", 'red', file=sys.stderr )
            Exception.__init__(self, *args, **kwargs)
