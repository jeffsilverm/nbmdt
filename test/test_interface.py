#! /usr/bin/python3
#
from unittest import mock
from unittest import patch
import interface

def test_init():
    interface_name = "eno1"
    eno1_obj = interface.Interface( interface_name )
    assert eno1_obj.name == interface_name

def test_get_mtu():
    with patch('



