#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An object of class Reliability has a value, reliability, which is from 0.0 to
# 1.0 inclusive, float(NaN) if not known, and has the shortcuts True and False
# for 1.0 and 0.0, respectively.

import operator
import typing
import sys
if __name__ == "__main__":
    try:
        import nosetests
        white_box_test = True
    except ImportError as e:
        print("nosetests cannot be imported - no white box testing will be done")
        white_box_test = False

    print ("Currently running python {sys.version_info}")
assert sys.version_info.major >= 3, "Not running python 3 ( at least), version"\
                                        "is {sys.version_info}"


class Reliability(operator):

    Tr = typing.Union( float, bool)

    def __init__(self, reliable: 'Tr') -> None :
        """Create an object of type reliability"""

        if not self.validate(reliable):
            raise ValueError("input to Reliability constructor out of range")
        self.false = False
        self.true = True
        self.reliability = reliable

    @staticmethod
    def validate(self, reliability: Tr) -> bool :
        """Return True if reliability is of type bool, or if reliability is
        in the range of 0.0 to 1.0 inclusively 
        
        :type   reliability
        :returns    bool"""

        return isinstance(reliability, bool) or 0.0 <= reliability <= 1.0

    def add(self, addend: Tr) -> Tr:
        """Returns a reliability.  This is an implementation of the OR function

        :type       addend : reliable.Reliability
        :returns    reliability
        :raises     AssertionError  if the result is not a valid reliability"""

        r = (self.reliability + addend) - (self.reliability * addend)
        assert self.validate(r)
        return r






