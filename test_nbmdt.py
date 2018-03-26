#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The Network Boot Monitor Diagnostic tool testing class
#

import sys
from typing import List

import pytest

import nbmdt

assert sys.version_info.major >= 3 and sys.version_info.minor >= 6, "Python must be later than version 3.6, " \
                                                                    f"is currently {str(sys.version_info)} "

def test_argparse():
    """Verify that the argparser accepts one and only one of --boot, --monitor, --diagnose"""

    def find_multiple_args(args_list: List[str]):
        """
        :param args_list:   list of strings
        :return:
        """
        sys.argv = ["nbmdt.py"] + args_list
        with pytest.raises(ValueError):
            parsed_args = nbmdt.arg_parser()
            assert parsed_args is None, f"There was a deliberate args parse error, this code comes after the " \
                                        f"exception was supposed to be raised. parsed_args should " \
                                        f"be None but is {str(parsed_args)} " \
                                 f"args_list is {str(args_list)}"

    sys.argv = ["nbmdt.py", "--boot"]
    args = nbmdt.arg_parser()
    assert isinstance(args, tuple), f"The return from nbmdt.arg_parser should be a tuple but is {str(type(args))}"
    assert len(args)==2, f"The return from nbmdt.arg_parser should be a length 2 but is {len(args)}"
    assert args.boot, "the --boot switch is False when it should be True"
    assert not args.monitor, "the --monitor switch is True when it should be False"
    assert not args.diagnose, "the --diagnose switch is True when it should be False"

    sys.argv = ["nbmdt.py", "--monitor"]
    args = nbmdt.arg_parser()
    assert isinstance(args, tuple), f"The return from nbmdt.arg_parser should be a tuple but is {str(type(args))}"
    assert len(args)==2, f"The return from nbmdt.arg_parser should be a length 2 but is {len(args)}"
    assert not args.boot, "the --boot switch is True when it should be False"
    assert args.monitor, "the --monitor switch is False when it should be True"
    assert not args.diagnose, "the --diagnose switch is False when it should be True"

    sys.argv = ["nbmdt.py", "--diagnose"]
    args = nbmdt.arg_parser()
    assert isinstance(args, tuple), f"The return from nbmdt.arg_parser should be a tuple but is {str(type(args))}"
    assert len(args)==2, f"The return from nbmdt.arg_parser should be a length 2 but is {len(args)}"
    assert not args.boot, "the --boot switch is True when it should be False"
    assert not args.monitor, "the --monitor switch is True when it should be False"
    assert args.diagnose, "the --diagnose switch is False when it should be True"

    find_multiple_args(["--diagnose", "--boot"])
    find_multiple_args(["--diagnose", "--monitor"])
    find_multiple_args(["--boot", "--monitor"])
    find_multiple_args(["--boot", "--diagnose"])
    find_multiple_args(["--monitor", "--boot", "--diagnose"])
    find_multiple_args([])


"""
class TestIPv4Route (pytest.TestCase ):

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
        # "This test makes sure that every route has an interface associated with it"
        for r in self.route_list:
            self.assertTrue (r.ipv4_interface in self.interface_list )

        for interface in self.interface_list :
            for route in self.route_list :
                if interface == route.ipv4_interface :
                    break
            else :
                raise AssertionError("interface {} was not found in the list of routes".format(interface) )

"""

if __name__ == "__main__":
    pytest.main()
