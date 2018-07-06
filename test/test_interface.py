#! /usr/bin/python3
#


import datetime
from platform import system
import pytest
from unittest.mock import patch
from pdb import set_trace

import interface

# This is all wrong -  I am trying to mock a class constructor.

# These derive from ../docs/nbmdt_test_plan.html#mozTocId811582
@pytest.mark.parametrize("interface,expected", [
    ("eno1",  "1: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000"\ 
   "link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 "\
   "gso_max_size 65536 gso_max_segs 65535"  ),
    ("eno2", "3: eno2: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN mode " \
                                "DEFAULT group default qlen 1000\    link/ether 00:10:18:cc:9c:77 brd " \
                                "ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 5 numrxqueues 5 " \
                                "gso_max_size 65536 gso_max_segs 65535"),
    # Test this:
    ("eno3", "4: eno3: <BROADCAST,MULTICAST> mtu 1500 qdisc mq state DOWN mode " \
                                "DEFAULT group default qlen 1000\    link/ether 00:10:18:cc:9c:77 brd " \
                                "ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 5 numrxqueues 5 " \
                                "gso_max_size 65536 gso_max_segs 65535")
    ])
@patch("utilities.OsCliInter.run_command")
def test_interface (if_ut, expected):
    assert if_ut.name == interface_name, f"eno1_obj.name should be {interface_name} but is actually {eno1_obj.name}"
    assert hasattr(eno1_obj, "mtu"), f"eno1_obj does not have an 'mtu' aatribute"


@patch("utilities.OsCliInter.run_command")
def test_init_eno1(mock_run_command):
    # Arrange
    interface_name: str = "eno1"
    mock_run_command.return_value = """3: """ + interface_name + """ <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc 
    fq_codel state UP 
    mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 
    addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535"""

    """
    jeffs@jeffs-desktop:/home/jeffs/python/nbmdt/test  (development) *  $ ip --details --oneline link show eno1
    3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\ 
       link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 
       gso_max_size 65536 gso_max_segs 65535 
    jeffs@jeffs-desktop:/home/jeffs/python/nbmdt/test  (development) *  $ 
    
    """

    # action
    eno1_obj = interface.Interface(interface_name)

    # Assert that the test passed
    assert eno1_obj.name == interface_name, f"eno1_obj.name should be {interface_name} but is actually {eno1_obj.name}"
    assert hasattr(eno1_obj, "mtu"), f"eno1_obj does not have an 'mtu' aatribute"
    assert eno1_obj.mtu == '1500',  f"eno1_obj.mtu should be 1500 but is actually {eno1_obj.mtu}"
    assert eno1_obj.state_up
    assert eno1_obj.broadcast
    assert eno1_obj.lower_up
    assert eno1_obj.brd == "ff:ff:ff:ff:ff:ff"
    delta_time = abs(eno1_obj._timestamp - datetime.datetime.now())
    limit = 10000
    assert abs(delta_time) < datetime.timedelta(0, 0, limit), \
        f"it took longer than f{limit} microseconds to read interface eno1. {delta_time}"


@patch("utilities.OsCliInter.run_command")
def test_init_wifi(mock_run_command):
    interface_name = "wifi0"
    mock_run_command.return_value = """12: wifi0: <BROADCAST,MULTICAST,UP> mtu 1500 group default qlen 1\    
    link/ieee802.11 fc:f8:ae:e3:e4:73"""

    # action
    wifi0_obj = interface.Interface(interface_name)

    # Assert that the test passed
    assert wifi0_obj.name == interface_name
    assert wifi0_obj.mtu == '1500'
    assert wifi0_obj.state_up
    assert wifi0_obj.broadcast
    assert wifi0_obj.ether == "fc:f8:ae:e3:e4:73"


@patch("utilities.OsCliInter.run_command")
def test_init_eth0(mock_run_command):
    interface_name = "eth0"

    mock_run_command.return_value = "18: eth0: <> mtu 1500 group default qlen 1\    link / ether ec:f4:bb:12:ee:83"

    # action
    eth0_obj = interface.Interface(interface_name)
    # Assert that the test passed
    assert eth0_obj.name == interface_name
    assert eth0_obj.mtu == '1500'
    assert not eth0_obj.state_up  # This did fail
    assert not eth0_obj.broadcast  # This did fail
    assert eth0_obj.carrier
    assert eth0_obj.ether == "ec:f4:bb:12:ee:83", f"MAC address not ec:f4:bb:12:ee:83 but {eth0_obj.ether}"


@patch("utilities.OsCliInter.run_command")
def test_init_enp3s0(mock_run_command):
    interface_name = "enp3s0"
    mock_run_command.return_value = "2: enp3s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN mode " \
                                    "DEFAULT group default qlen 1000\    link/ether 00:10:18:cc:9c:77 brd " \
                                    "ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 5 numrxqueues 5 " \
                                    "gso_max_size 65536 gso_max_segs 65535"

    enp3s0_obj = interface.Interface(interface_name)
    try:
        # Assert that the test passed
        assert enp3s0_obj.name == interface_name
        assert hasattr(enp3s0_obj, 'carrier')
        assert not enp3s0_obj.carrier, f"enp3s0 No carrier"  # This failed
        assert hasattr(enp3s0_obj, 'lower_up'), "enp3s0 No attribute lower_up"
        assert not enp3s0_obj.lower_up, "enp3s0 lower_up is True and should be False"
        assert not enp3s0_obj.state_up, f"enp3s0 state_up should be False but state_up is True instead"
        assert enp3s0_obj.ether == "00:10:18:cc:9c:77", f"enp3s0.ether should be 00:10:18:cc:9c:77 but is {enp3s0_obj.ether}"
        assert enp3s0_obj.brd == "ff:ff:ff:ff:ff:ff", f"enp3s0_obj.brd should be ff:ff:ff:ff:ff:ff but is {enp3s0_obj.brd}"
    except AssertionError as a:
        print("test failed.  mock_run_command.return_value is \n" +
              mock_run_command.return_value + "\n"
              "The enp3s0 object is " + enp3s0_obj.__str__() )
        raise

@patch("utilities.OsCliInter.run_command")
def test_run_eno1(mock_run_command):
    args : tuple = mock_run_command.call_args
    # args is a 2 element tuple.  The first element is a tuple of all of the arguments that were not labeled
    # The second element is a dictionary of all of the arguments that were labeled.
    # For example:
    """
>>> import unittest.mock
>>> mock = unittest.mock.Mock()
>>> mock("sd", 3, red=True)
<Mock name='mock()' id='140245555639912'>
>>> mock.call_args
call('sd', 3, red=True)
>>> 3 in mock.call_args   # Wrong way to do this!
False
>>> 3 in mock.call_args[0]
True
>>> 'red' in mock.call_args[1]
True
>>> mock.call_args[0]
('sd', 3)
>>> 

    """
    if "--stats" in args[0]:
        # Have to show some changes
        mock_run_command.return_value = "3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP" \
            "mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff\    " \
            "RX: bytes  packets  errors  dropped overrun mcast   \    250298130  213503   0       0       0       616     \    " \
            "TX: bytes  packets  errors  dropped carrier collsns \    13175231   110321   0       0       0       0"
        yield
        mock_run_command.return_value = "3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP" \
            "mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff\    " \
            "RX: bytes  packets  errors  dropped overrun mcast   \    250299999  229999   0       0       0       616     \    " \
            "TX: bytes  packets  errors  dropped carrier collsns \    13178888   110888   0       0       0       0"
    else:
        mock_run_command.return_value = "3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP" \
            "mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff"


@patch("utilities.OsCliInter.run_command")
@patch("platform.system")
def test_init_en0(mock_run_command, mock_platform_system):
    system.return_value = "Darwin"
    interface_name = "en0"
    en0_obj = interface.Interface(interface_name)
    # for now
    assert True


if __name__ == "__main__":
    test_interface("eno1")
    test_interface("eno2")
    test_init_eno1()
    test_init_wifi()
    test_init_eth0()
    test_init_en0()  # Macintosh

    test_run_eno1()

