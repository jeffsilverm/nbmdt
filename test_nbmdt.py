#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool testing class
#

import unittest
import nbmdt


class TestIPv4Route (unittest.TestCase ):

    def setUP(self):
        self.route_list = nbmdt.IPv4_route.find_ipv4_routes()
        self.interface_list = nbmdt.Interfaces.find_interfaces()


    def test_all_are_routes(self):
        for r in self.route_list:
            self.assertIsInstance(r, nbmdt.IPv4_route )

    def test_route_0_dest_default (self ):
        self.assertTrue(self.route_list[0]=="default" or self.route_list[0]=="0.0.0.0")

    def test_jeffs_desktop(self ):
        # ipv4_destination, ipv4_gateway, ipv4_mask, ipv4_flags, ipv4_metric, ipv4_ref, ipv4_use, ipv4_interface
        self.assertEqual(self.route_list[0].ipv4_interface, "eno1")
        self.assertEqual(self.route_list[0].ipv4_ipv4_gateway, "192.168.1.1")

    def test_all_ipv4_routes_found(self):
        """This test makes sure that every route has an interface associated with it"""
        for r in self.route_list:
            self.assertTrue (r.ipv4_interface in self.interface_list )

        for interface in self.interface_list :
            for route in self.route_list :
                if interface == route.ipv4_interface :
                    break
            else :
                raise AssertionError("interface {} was not found in the list of routes".format(interface) )



if __name__ == "__main__" :
    unittest.main()

