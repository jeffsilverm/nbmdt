#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# test class interfaces.PhysicalInterace

from interfaces import PhysicalInterface
from unittest.mock import patch


def fake_run_ip_link_command(interface=None) -> dict:
    """
    This subroutine is to be run instead of the real
    PhysicalInterfaces.run_ip_link_command
    :param interface: str   name of the interface to test
    :return:
    """

    if interface == "enx1":
        answer = {"enx1": "<NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 "
                          r"qdisc fq_codel state DOWN mode DEFAULT group default "
                          r"qlen 1000\      link/ether 00:22:4d:7c:4d:d9 "
                          r"brd ff:ff:ff:ff:ff:ff\ "
                          r"RX: bytes  packets  errors  dropped overrun mcast   \    0"
                          r" \ 0        0       0       0       0       \    "
                          r"TX: bytes  packets  errors  dropped carrier collsns \ "
                          r"0          0        0       0       0       0"}
        return answer
    else:
        return {interface: f"Haven't done {interface} yet."}


def test_interfaces():
    mocked_interface = "enx1"
    print(f"The object ID of the fake_run_ip_link_command method is {id(fake_run_ip_link_command)}")
    print(
        f"The object ID of the interfaces.PhysicalInterface.run_ip_link_command is "
        f"{id(PhysicalInterface.run_ip_link_command)}")
    print("The results of the PhysicalInterface.run_ip_link_command call on eno1 is:\n" + str(
        PhysicalInterface.run_ip_link_command("eno1")))
    with patch("interfaces.PhysicalInterface.run_ip_link_command") as run_ip_link_command_mock:
        # fake_run_ip_link_command is not a call, it's a callable
        run_ip_link_command_mock.return_value = fake_run_ip_link_command
        print(
            f"After patching, the object ID of the interfaces.PhysicalInterface.run_ip_link_command is "
            f"{id(PhysicalInterface.run_ip_link_command)}")
        if_properties_dict = PhysicalInterface.run_ip_link_command(mocked_interface)
        if callable(if_properties_dict):
            print(f"if_properties_dict is callable.  If we call it,\n{if_properties_dict()} . ")
            print(f"If we call it with enx1: {PhysicalInterface.run_ip_link_command('enx1')}.")
        assert isinstance(if_properties_dict, dict), \
            f"if_properties_dict should be a dict, but it's really a " + \
            str(type(if_properties_dict))
        print(if_properties_dict)
