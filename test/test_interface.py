#! /usr/bin/python3
#


from unittest import mock
from unittest.mock import patch


import interface
import utilities

@patch("utilities.OsCliInter.run_command")
def test_init(mock_run_command):
    # Arrange
    interface_name = "eno1"
    mock_run_command.return_value="""3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535"""

    """
    jeffs@jeffs-desktop:/home/jeffs/python/nbmdt/test  (development) *  $ ip --details --oneline link show eno1
    3: eno1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000\    link/ether 00:22:4d:7c:4d:d9 brd ff:ff:ff:ff:ff:ff promiscuity 0 addrgenmode none numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
    jeffs@jeffs-desktop:/home/jeffs/python/nbmdt/test  (development) *  $ 
    
    """

    # action
    eno1_obj = interface.Interface( interface_name )

    # Assert that the test passed
    assert eno1_obj.name == interface_name

if __name__ == "__main__":
    test_init()



