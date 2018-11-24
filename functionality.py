#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#

from typing import TypeVar, Union


class Functionality:
    """
    Functionality implements an opaque data type that represents the functionality of an entity.  The functionality of
    an entity has 2 parts (this implementation has only 1 part): performance and risk (this implementation does not
    implement risk).  Examples of factors that can lead to poor performance include but are not limited to:
    * Network errors: dropped packets, runts, collisions, retransmits
    * High CPU utilitization
    * Excessive disk I/O rates
    """
    F = TypeVar("Functionality")

    def __init__(self, initial: float = 0.0, risk: Union[float, None] = 0.0) -> None:
        """
        Create a functionality object
        :param initial  The initial value of functionality, which varies from 0.0 (dead) to 1.0 (fully
        functioning).
        :param risk    The risk that the entity will fail shortly.  Ignored for now.  0.0 means completely reliable,
                        0.5 means 50% chance of failure, 1.0 means it has failed.  If None, then no value
        """
        self.functionality = initial
        self.risk = risk

    def __or__(self, other: F) -> F:
        """
        Returns the logical OR (inclusive) of self and the other object
        :param other:
        :return:
        """

        if not isinstance(other, Functionality):
            raise TypeError(f"The other is type {type(other)}, should be functionality")
        r = self.functionality + other.functionality - self.functionality * other.functionality
        assert 0.0 <= r <= 1.0, f"r is {r}, should be between 0.0 and 1.0 inclusive"
        return self.__init__(initial=r, risk=None)

    def __and__(self, other: F) -> F:
        """
        Returns the logical AND of self and the other object
        :param other:
        :return:
        """

        if not isinstance(other, Functionality):
            raise TypeError(f"The other is type {type(other)}, should be functionality")
        r = self.functionality * other.functionality
        assert 0.0 <= r <= 1.0, f"r is {r}, should be between 0.0 and 1.0 inclusive"
        return self.__init__(initial=r, risk=None)

    def __add__(self, other: F) -> F:
        """
        Returns the logical OR (inclusive) of self and the other object, but as an operator so when can create boolean
        algebraic equations.
        :param other:
        :return:
        """
        r = self.__or__(other)
        return r

    def __mul__(self, other: F) -> F:
        """
        Returns the logical AND of self and the other object, but as an operator so when can create boolean
        algebraic equations.
        :param other:
        :return:
        """
        r = self.__and__(other)
        return r
