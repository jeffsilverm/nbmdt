#! /usr/bin/python3.6


import unittest
import reliability
from typing import Union


class UnittestReliability(unittest.TestCase):
    Tr = reliability.Reliability
    Tu = Union(float, bool)

    def __init__(self, value: Tr = float('nan')) -> None:
        """
        :type value: self.Tu
        """
        super(self).__init__(value)

    @staticmethod
    def test_constructor(self: object, test_value: Tr) -> object:
        r: UnittestReliability = reliability.Reliability(reliable=test_value)
        assert UnittestReliability.validate(r), \
            "Reliability constructor created an invalid value, {r}"
        return True


ur = UnittestReliability()
ur.test_constructor(test_value=0.5)
ur.test_constructor(test_value=1.0)
ur.test_constructor(test_value=0.0)
ur.test_constructor(test_value=True)
ur.test_constructor(test_value=False)
ur.test_constructor(test_value=1.01)
ur.test_constructor(test_value=-0.01)
