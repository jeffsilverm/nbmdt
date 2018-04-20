#! /usr/bin/python3
#


# from unittest import mock
from unittest.mock import patch

import interface


@patch("utilities.OsCliInter.run_command")
def test_init_eno1(mock_run_command):
    # Arrange
    interface_name = "eno1"
    mock_run_command.return_value = """3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535"""

    """
    jeffs@jeffs-desktop:/home/jeffs/python/nbmdt/test  (development) *  $ ip --details --oneline link show eno1
    3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
    jeffs@jeffs-desktop:/home/jeffs/python/nbmdt/test  (development) *  $ 
    
    """

    # action
    eno1_obj = interface.Interface(interface_name)

    # Assert that the test passed
    assert eno1_obj.name == interface_name
    assert eno1_obj.mtu == '1500'
    assert eno1_obj.state_up
    assert eno1_obj.broadcast


@patch("utilities.OsCliInter.run_command")
def test_init_wifi(mock_run_command):
    interface_name = "wifi0"
    mock_run_command.return_value = """12: wifi0: <BROADCAST,MULTICAST,UP> mtu 1500 group default qlen 1\    link/ieee802.11 fc:f8:ae:e3:e4:73"""

    # action
    wifi0_obj = interface.Interface(interface_name)

    # Assert that the test passed
    assert wifi0_obj.name == interface_name
    assert wifi0_obj.mtu == '1500'
    assert wifi0_obj.state_up
    assert wifi0_obj.broadcast


"""
@patch("utilities.OsCliInter.run_command")
def test_init_eth0(mock_run_command):
    interface_name = "eth0"

    mock_run_command.return_value = "18: eth0: <> mtu 1500 group default qlen 1\    link / ether ec:f4:bb:12:ee:83"

    # action
    eth0_obj = interface.Interface(interface_name)
    # Assert that the test passed
    assert eth0_obj.name == interface_name
    assert eth0_obj.mtu == '1500'
    assert eth0_obj.state_up
    assert eth0_obj.broadcast


@patch("utilities.OsCliInter.run_command")
@patch("platform.system")
def test_init_en0(mock_run_command, mock_platform_system):
    interface_name = "en0"
    # For now
    return True

"""

if __name__ == "__main__":
    test_init_eno1()
#    test_init_wifi()
#    test_init_eth0()
#    test_init_en0()     # Macintosh
