#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
from enum import Enum
# Issue 5 renamed IPv4_address to IPv4Address and IPv6_address to IPv6Address
# Tracking down a pesky import problem
# from network import IPv4Address as ipv4
# from network import IPv6Address as ipv6
from socket import AF_INET, AF_INET6
from typing import List

import layer
from constants import ErrorLevels


class Transport(object):
    """A class for monitoring transports: TCP, UDP

    """

    def get_status(self) -> ErrorLevels:
        return self.layer.get_status()

    @classmethod
    def discover(cls):
        return "A discovered set of transports"

    class TransportNames(Enum):
        # Values from /etc/protocols
        TCP = 6
        UDP = 17

    class TcpConnection(object):

        def __init__(self, ip_proto, src_host, src_port, dst_host, dst_port) -> None:
            if ip_proto != socket.AF_INET and ip_proto != socket.AF_INET6:
                raise ValueError("ip_proto may be AF_INET or AF_INET6, but not " + str(ip_proto))
            self.ip_proto = ip_proto
            self.src_host = src_host
            self.src_port = src_port
            self.dst_host = dst_host
            self.dst_port = dst_port

    def __init__(self, connections: List[TcpConnection]) -> None:
        self.connections: connections
        pass

    def find_all_listeners(self, transport: TransportNames = TransportNames.TCP) -> dict:
        pass

    def add_connection(self, source_port: int, destination_port: int,
                       #                       remote_address : Union[ipv4, ipv6],
                       remote_address,
                       transport: TransportNames = TransportNames.TCP) -> None:
        connection = (source_port, destination_port, remote_address, transport)
        self._connections.append(connection)

    @property
    def list_all_connections(self) -> list:
        return self._connections

    @classmethod
    def find_all_connections(cls, transport=TransportNames.TCP, af_family=None) -> list:
        """


        :return: A list of all of the connections.  Each connection is a
        """
        if af_family != AF_INET and af_family != AF_INET6 and af_family is not None:
            raise ValueError("af_family has a bad value " + str(af_family))
        print(transport)
        return []


if __name__ == "__main__":
    transports: Transport = Transport.discover()
    print(transports)
