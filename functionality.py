#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

from typing import TypeVar, Union
import sys


class Functionality:
    """
    Functionality implements an opaque data type that represents the functionality of an entity.  The functionality of
    an entity has 2 parts (this implementation has only 1 part): performance and risk (this implementation does not
    implement risk).  Examples of factors that can lead to poor performance include but are not limited to:
    * Network errors: dropped packets, runts, collisions, retransmits
    * High CPU utilitization
    * Excessive disk I/O rates
    """
    # F = TypeVar("F")

    def __init__(self, initial: float, risk: Union[float, None] = 0.0) -> None:
        """
        Create a functionality object
        :param initial  The initial value of functionality, which varies from 0.0 (dead) to 1.0 (fully
        functioning).
        :param risk    The risk that the entity will fail shortly.  Ignored for now.  0.0 means completely reliable,
                        0.5 means 50% chance of failure, 1.0 means it has failed.  If None, then no value
        """
        try:
            initial = float(initial)
        except ValueError as v:
            raise TypeError(f"Can't convert type {type(initial)} value {initial} to a float")
        if initial < 0.0 or initial > 1.0:
            raise ValueError(f"The initial value must be in the range of 0.0 to 1.0, inclusive, not {initial}")
        self.functionality = initial
        self.risk = risk if risk is not None else 0.0

    def __str__  ( self ) -> str:
        # For now.  Figure out how to do risk, later.
        return str(self.functionality)

    def __or__(self, other: 'Functionality') -> 'Functionality':
        """
        Returns the logical OR (inclusive) of self and the other object
        :param other:
        :return:
        """

        if not isinstance(other, Functionality):
            raise TypeError(f"The other is type {type(other)}, should be functionality")
        r = self.functionality + other.functionality - self.functionality * other.functionality
        assert 0.0 <= r <= 1.0, f"r is {r}, should be between 0.0 and 1.0 inclusive"
        q = Functionality(initial=r, risk=None)
        return q

    def __and__(self, other ) -> 'Functionality':
        """
        Returns the logical AND of self and the other object
        :param other:
        :return:
        """

        if not isinstance(other, Functionality):
            print(f"other should be an instance of Functionality, and is actually {type(other)}", file=sys.stderr)
            other = Functionality(other)
        r = self.functionality * other.functionality
        assert 0.0 <= r <= 1.0, f"r is {r}, should be between 0.0 and 1.0 inclusive"
        q = Functionality(initial=r, risk=None)
        return q

    def __add__(self, other: 'Functionality') -> 'Functionality':
        """
        Returns the logical OR (inclusive) of self and the other object, but as an operator so when can create boolean
        algebraic equations.
        :param other:
        :return:
        """
        r = self.__or__(other)
        assert isinstance(r, "Functionality"), f"r is of type {type(r)}, should be Functionality"
        return r

    def __mul__(self, other: 'Functionality') -> 'Functionality':
        """
        Returns the logical AND of self and the other object, but as an operator so when can create boolean
        algebraic equations.
        :param other:
        :return:
        """
        r = self.__and__(other)
        assert isinstance(r,Functionality), f"r is of type {type(r)}, should be Functionality"
        return r


if "__main__" == __name__:
    ac = .5
    bc = .8
    a = Functionality(ac)
    b = Functionality(bc)
    fw = (a and b)
    bw = (b and a)
    assert fw.functionality == bw.functionality , f" 'and' is not commutative, {a and b} {b and a}"
    print(f".5 * .6 should be .3, is {(a*b).functionality}")
    print(f".6 * .5 should be .3, is {(b*a).functionality}")
    print(f"Type of * should be {type(Functionality(.1))}, is {type(a*b)}")
    assert ( a * b ).functionality == ac * bc, f"( a * b ).functionality is {( a * b ).functionality} should be {ac*bc}"
    assert ( a * b ).functionality == (b * a ).functionality, f" '*' is not commutative, {a * b} {b * a}"
    assert ( a and b ).functionality == (b and a ).functionality, f" 'and' is not commutative, {a and b} {b and a}"
    assert ( a and b ).functionality == ac * bc, f"( a and b ).functionality is {( a and b ).functionality} should be {ac*bc}"