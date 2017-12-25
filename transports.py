#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
# Issue 5 renamed IPv4_address to IPv4Address and IPv6_address to IPv6Address
from network import IPv4Address as ipv4
from network import IPv6Address as ipv6
from socket import AF_INET, AF_INET6
from typing import Union


class Transports(object):
    """A class for monitoring transports: TCP, UDP

    """
    class TransportNames(Enum):
        TCP = 1
        UDP = 2

    def __init__(self, configuration_file: str = None) -> None:
        self._connections : list = list()
        pass

    def find_all_listeners(self, transport : TransportNames = TransportNames.TCP) -> dict:
        pass

    """
    def find_all_connections(self, transport : TransportNames = TransportNames.TCP) -> dict:
        pass
    """

    def add_connection(self, source_port : int, destination_port : int,
                       remote_address : Union[ipv4, ipv6],
                       transport : TransportNames = TransportNames.TCP ) -> None:
        connection = ( source_port, destination_port, remote_address, transport )
        self._connections.append(connection)

    @property
    def list_all_connections(self) -> list:
        return self._connections

    def find_all_connections(self, transport=TransportNames.TCP, af_family=None) -> list:

        """


        :return: A list of all of the connections.  Each connection is a
        """
        if af_family != AF_INET and af_family != AF_INET6 and af_family is not None:
            raise ValueError ("af_family has a bad value "+str(af_family) )
        return []


if __name__ == "__main__":
    transports = Transports()
    print( transports.find_all_connections())








