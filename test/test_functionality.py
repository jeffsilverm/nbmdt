#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Test for class Functionality
from functionality import Functionality as func

def test_or ( a, b ) -> func:
    """Returns the functionality of a or b (inclusive or)
    :param  a, b    the functional values
    """

    pass

def test_and ( a , b ) -> func:
    """Returns the functionality of a and b
        :param  a, b    the functional values
        """
    r = a * b
    return r

if "__main__" == __name__:
    a = Functionality(.5)
    b = Functionality(.6)
    print(f".5 * .6 should be .3, is {a*b}")
    print(f".6 * .5 should be .3, is {b*a}")
    print(f"Type of * should be 'Functionality', is {type(a*b)}")

