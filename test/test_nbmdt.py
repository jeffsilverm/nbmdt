#! /usr/bin/python3
#


from platform import system
# from unittest import mock
from unittest.mock import patch
import datetime

import sys
import nbmdt

def test_boot_option():
    """
    Test that nbmdt --boot option works
    :return:
    """
    sys.argv=["--boot"]
    nbmdt.main(test=True)




if __name__ == "__main__":
    test_boot_option()
    test_daemon_option()
    test_diagnose_option()
    test_nominal_option()
    test_monitor_option()
    test_configuration_file_option()
