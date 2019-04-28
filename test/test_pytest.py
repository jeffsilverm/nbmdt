#! /usr/bin/env python3
# _*_ coding: utf-8 -*-

# This file tests that pytest is running the correct version of python3.
# Should be at least python 3.6
from __future__ import print_function
import sys

def test_pytest():
    assert sys.version_info.major == 3,  \
        40*'*'+"\nPython version is NOT 3, it's "+str(sys.version_info.major)+"\n" + 40*'='
    assert sys.version_info.minor >= 6,  \
        40*'#'+"Python minor version is less than 6, it's "+str(sys.version_info.minor)+"\n" + 40*"+"
    if sys.version_info. major == 3 and sys.version_info.minor >= 6 :
        print ( "python version " + sys.version.split()[0] +"  is acceptable", file=sys.stderr )
    else:
        print ( "python version " + sys.version.split()[0] +" WILL FAIL!", file=sys.stderr )
        sys.exit(27)

if "__main__" == __name__ :
    test_pytest()
