#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# An object of class Reliability has a value, reliability, which is from 0.0 to
# 1.0 inclusive, float(NaN) if not known, and has the shortcuts True and False
# for 1.0 and 0.0, respectively.

import operator
import sys
from typing import Union

if __name__ == "__main__":
    try:
        import nosetests
        white_box_test = True
    except ImportError as e:
        print("nosetests cannot be imported - no white box testing will be done")
        white_box_test = False

    print("Currently running python {}".format(sys.version_info))
assert sys.version_info.major >= 3, "Not running python 3 ( at least), version" \
                                    "is {sys.version_info}"


class Reliability():
    """
    Class Reliability defines a data type that is a measure of the reliability of an object.  When in an operational
    mode (boot or monitor) or in simulation mode, "reliability" is a measure of how many redundant dependencies are up.
    When in design mode, reliability is a measure of the predicted reliability, which is related to the instrinsic
    reliability of the object and to the reliability of the dependencies.
    """
    Tr = Union[float, bool]

    def __init__(self: None, reliable: 'Tr') -> None:

        """Create an object of type reliability"""

        if not self.validate(reliable):
            raise ValueError("input to Reliability constructor out of range")
        self.false = False
        self.true = True
        self.reliability = reliable

    @staticmethod
    def validate(reliability: Tr) -> bool:
        """Return True if reliability is of type bool, or if reliability is
        in the range of 0.0 to 1.0 inclusively 

        :type   reliability Tr
        :returns    bool

        """

        return isinstance(reliability, bool) or 0.0 <= reliability <= 1.0

    def __add__(self, other: Union[Tr, 'Reliability']) -> Tr:
        """Returns a reliability.  This is an implementation of the OR function

        :type       other : reliable.Reliability
        :returns    reliability
        :raises     AssertionError  if the result is not a valid reliability"""

        if isinstance(other, Reliability):
            r = (self.reliability + other.reliability) - (self.reliability * other.reliability)
        elif isinstance(other, float):
            r = (self.reliability + other) - (self.reliability * other)
        elif isinstance(other, bool):
            r = 1.0 if other else self.reliability
        assert self.validate(r)
        return r

    def __radd__(self, other: Union[Tr, 'Reliability']) -> Tr:
        """Returns a reliability.  This is an implementation of the OR function but the order of the operands is swapped

        :type       other : reliable.Reliability
        :returns    reliability
        :raises     AssertionError  if the result is not a valid reliability
        """
        assert isinstance( other, float) or isinstance(other, bool) or isinstance(other, Reliability), \
            "other is not an acceptable type.  It is really, {}".format(type(other))
        return other.__add__ (self.reliability )


if __name__ == "__main__":
    def test_Reliability ( value: float, correct: bool ) -> bool:
        """This subroutine tests that the Reliability constructor will throw a ValueError exception when given a bad
        value or a bad type
        :type       float   value
        :type       bool    correct True if this call should work, False if Reliability should raise ValueError
        :returns    bool    True if the constructor works properly, False otherwise
        """
        try:
            r = Reliability(value)
            if correct:
                print("Reliability did not raise an exception because it was given a good value {value}", \
                  file=sys.stderr)
                return True
            else:
                print("FAIL! Reliability raised an exception although it should not have {value}", \
                     file=sys.stderr)
                return False
        except ValueError as e:
            if correct:
                print("FAIL! Reliability did not raise an exception although it should have {value}", \
                     file=sys.stderr)
                return False
            else:
                print("Reliability raised a ValueError exception because it was given a bad value {value}", \
                  file=sys.stderr)
                return True


    s1 = Reliability(.5)
    s2 = Reliability(.4)
    r = s1 + s2
    assert r == 0.7, "Adding a reliability and a reliability gave the wrong answer, should be .7 is {:f}".format(r)
    print("Adding two reliabilities works", file=sys.stderr)
    r = s1 + .4
    assert r == 0.7, "Adding a reliability and a float gave the wrong answer, should be .7 is  {:f}".format(r)
    print("Adding a reliability and a float works", file=sys.stderr)
    r = .4 + s1
    assert r == 0.7, "Adding a float and a reliability gave the wrong answer, should be .7 is  {:f}".format(r)
    print("Adding a float and a reliability works", file=sys.stderr)


    test_Reliability(1.01)        # Out of range but allowed type, should be detected only at run time
    test_Reliability(-0.01)       # Out of range but allowed type, should be detected only at run time
    test_Reliability(1)           # Bad type, should be detected with mypy, pycharm, or at run time
    test_Reliability(True)        # Correct
    test_Reliability(False)       # Correct
    test_Reliability("0.5")       # Bad type, should be detected with mypy, pycharm, or at run time


