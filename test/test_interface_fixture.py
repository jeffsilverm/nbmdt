#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import interface
import sys
import pdb


def run_command(intf: str) -> str:
    print("in run_command in test_interface_fixture: intf is " + intf, file=sys.stderr)
    if intf == "eno1" or "eno1" in intf:
        result = """3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP 
    mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 
    addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535"""
    else:
        raise NotImplementedError
    return result


@pytest.fixture()
def create_fixture():
    """Create a fixture that will test an ethernet interface"""
    return run_command


def test_init_eno1():
    """Test interface eno1"""
    interface_name = "eno1"
    # interface.Interface will invoke the run_command method
    pdb.set_trace()
    eno1_obj = interface.Interface(interface_name)
    assert eno1_obj.lower_up

if __name__ == "__main__":
    pdb.set_trace()
    test_init_eno1()



