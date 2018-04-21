#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import interface

@pytest.fixture()
def run_command(intf):
    """Arrange to test interface eno1"""
    # Arrange
    if intf == "eno1":
        return """3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP 
    mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 
    addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535"""
    else:
        raise NotImplementedError

def test_init_eno1(run_command):
    """Test interface eno1"""
    interface_name = "eno1"
    eno1_obj = interface.Interface(interface_name)
    assert eno1_obj.lower_up


