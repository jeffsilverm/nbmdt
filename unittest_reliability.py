#! /usr/bin/python3.6


import unittest
import reliability
from typing import Union


class UnittestReliability ( unittest.TestCase ):

    Tr = reliability.Reliability
    Tu = Union ( float, bool )

    def __init__(self, value:Tr = float('nan')) -> None:
        """
        :type value: self.Tu
        """
        super().__init__(value)


    def test_constructor (test_value:Tr) -> bool :

        r:UnittestReliability = reliability.Reliability(reliable=test_value)
        assert UnittestReliability.validate(r), \
            "Reliability constructor created an invalid value, {r}"
        return True


ur = UnittestReliability()
ur.test_constructor( 0.5 )
ur.test_constructor( 1.0 )
ur.test_constructor( 0.0 )
ur.test_constructor( True )
ur.test_constructor( False )
ur.test_constructor( 1.01 )
ur.test_constructor( -0.01 )
