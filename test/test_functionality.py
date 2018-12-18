#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Test for class Functionality
import sys
from typing import Any

import pytest

import functionality
from functionality import Functionality as Func

type_of_func = type(functionality.Functionality(.23))

def check_functionality(at: Any, value: float) -> bool:
    assert isinstance(at, functionality.Functionality), \
        f"The argument is type {type(at)}, should be type {type_of_func}"
    assert at.functionality == value, f"The argument should have functionality {value} but is {at.functionality}"
    return True

@pytest.mark.xfail(raises=[ValueError, TypeError] )
def test_invalid_initials():
    if False:
        print("Testing invalid initial values")
        x1 = Func(-0.1)  # Too small
        x2 = Func(1.1)  # Too large
        x3 = Func((.23 + .03j))  # Can't convert to float, complex
        x4 = Func('blech!')  # Can't convert to float, string
        return x1, x2, x3, x4

@pytest.mark.xfail(raises=ValueError )
def test_invalid_values():
    if False:
        print("Testing invalid initial values")
        x1 = Func(-0.1)  # Too small
        x2 = Func(1.1)  # Too large
        return x1, x2

@pytest.mark.xfail(raises=TypeError )
def test_invalid_types():
    if False:
        print("Testing invalid initial types")
        x3 = Func((.23 + .03j))  # Can't convert to float, complex
        x4 = Func('blech!')  # Can't convert to float, string
        return x3, x4


def test_constructor():
    print("In test_constructor", file=sys.stderr)
    with pytest.raises(ValueError, message="Should have raised a ValueError, and didn't") as p:
        x1 = Func(-0.123)  # Can't convert to float, string

    with pytest.raises(ValueError, message="Should have raised a ValueError, and didn't") as p:
        x2 = Func(1.1)  # Too large

    with pytest.raises(TypeError, message="Should have raised a TypeError, and didn't") as p:
        x3 = Func((.23 + .03j))  # Can't convert to float, complex

    with pytest.raises(TypeError, message="Should have raised a TypeError, and didn't") as p:
        x4 = Func('blech!')  # Can't convert to float, string

    r1 = Func(1.0).functionality
    r0 = Func(0.0).functionality
    assert r1 == Func(True).functionality, f"Func(True) should have returned 1.0, actually returned {Func(True)}"
    assert r0 == Func(False).functionality, f"Func(False) should have returned 0.0, actually returned {Func(False)}"
    assert r1 == Func(1).functionality, f"Func(1) should have returned 1.0, actually returned {Func(True)}"
    assert r0 == Func(0).functionality, f"Func(0) should have returned 0.0, actually returned {Func(False)}"
    with pytest.raises(ValueError, message="Should have raised a ValueError, and didn't") as p:
        x1 = Func(-1)  # Can't convert to float, string
    with pytest.raises(ValueError, message="Should have raised a ValueError, and didn't") as p:
        x2 = Func(2)  # Too large


def test_and():
    print("method test_and", file=sys.stderr)

    af = .5
    bf = .6
    a = Func(af)
    b = functionality.Functionality(bf)

    r = a.__and__(b)
    check_functionality(r, af * bf)
    r = b.__and__(a)
    check_functionality(r, af * bf)
    r = a and b
    check_functionality(r, af * bf)
    r = a * b
    check_functionality(r, af * bf)

def test_or():
    print("method test_or", file=sys.stderr)
    af = .5
    bf = .6
    a = Func(af)
    b = functionality.Functionality(bf)

    or_value = (af + bf) - (af * bf)
    r = a.__or__(b)
    check_functionality(r, or_value)
    r = b.__or__(a)
    check_functionality(r, or_value)
    r = a or b
    check_functionality(r, or_value)
    r = a + b
    check_functionality(r, or_value)



if "__main__" == __name__:
    print("Main testing", file=sys.stderr)

    with pytest.raises(ValueError, message="Should have raised a ValueError, and didn't") as p:
        x1 = Func(-0.123)  # Can't convert to float, string

    with pytest.raises(ValueError, message="Should have raised a ValueError, and didn't") as p:
        x2 = Func(1.1)  # Too large

    with pytest.raises(TypeError, message="Should have raised a TypeError, and didn't") as p:
        x3 = Func((.23 + .03j))  # Can't convert to float, complex

    with pytest.raises(TypeError, message="Should have raised a TypeError, and didn't") as p:
        x4 = Func('blech!')  # Can't convert to float, string



    af = .5
    bf = .6
    a = Func(af)
    b = functionality.Functionality(bf)
    check_functionality(a, af), \
        f"The constructor for Func(.5) returned a {type(a)} instead of " \
        f"functionality.Functionality.  Huh?"

    with pytest.raises(TypeError) as p1:
        x1m = Func(-0.2)
        x2m = Func(+1.2)
        x3 = Func((.02 + .0003j))  # Can't convert to float, complex
        x4 = Func('BLAM!')  # Can't convert to float, string


    print("Testing AND")
    r = a.__and__(b)
    check_functionality(r, af * bf)
    r = b.__and__(a)
    check_functionality(r, af * bf)
    r = a and b
    check_functionality(r, af * bf)
    r = a * b
    check_functionality(r, af * bf)

    print("Testing OR")
    or_value = (af + bf) - (af * bf)
    r = a.__or__(b)
    check_functionality(r, or_value)
    r = b.__or__(a)
    check_functionality(r, or_value)
    r = a or b
    check_functionality(r, or_value)
    r = a + b
    check_functionality(r, or_value)
