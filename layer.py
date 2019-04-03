import datetime
import sys
import time
import typing
import datetime

import pytest

import constants


class Layer(object):
    """
    A layer is a layer in the OSI or TCP stack.  A layer can do the following operations
    Record the moment the check was made, so that rates of counter changes can be recorded or logged
    Measure the difference between fields
    Return if two objects are equal EXCEPT for the time stamps which will likely be different
    delta time
    """

    def __init__(self, name: str) -> None:
        self.time = datetime.datetime.now()
        self.name = name  # name of the entity (NIC, nameserver, route, etc.) being recorded
        self.error_status = constants.ErrorLevels.UNKNOWN

    def get_status(self) -> constants.ErrorLevels:
        return constants.ErrorLevels.NORMAL

    def __sub__(self, other: 'Layer') -> 'Layer':
        """

        :param other: an object of class Layer or one of its children
        :return: an object of class Layer which has the differences between the two objects
        This method raises a ValueError exception of the name of the two objects are different.
        I struggled with the question of whether to raise an exception if the timestamps are in the "wrong" order
        and I decided against it.  My use case is (18-22)/-4 = 1 and (22-18)/4 = 1 so it really doesn't matter.
        """
        if not isinstance(other, Layer):
            raise ValueError(f"other should be a child of Layer, is actually {type(other)}")
        if type(self) != type(other):
            raise ValueError
        if self.name != other.name:
            raise ValueError(f"other.name is {other.name} but my name is {self.name}. Should be the same")
        result = Layer(name=other.name)  # noqa pycharm doesn't know that other is a Layer

        for at in self.__dict__:
            type_me = type(self.__getattribute__(at))
            type_other = type(other.__getattribute__(at))
            assert type_me == type_other, "type_me and type_other should be the same type and are not" \
                f"type_me is {type_me} while type_other is {type_other}."

            me_and_my_attribute_value = self.__getattribute__(at)
            him_and_hers_attribute_value = other.__getattribute__(at)
            if type_me == str and type_other == str:
                result_str = f"Me: {me_and_my_attribute_value}" + f"Him: {him_and_hers_attribute_value}"
                result.__setattr__(at, result_str)
            else:
                try:
                    # These might be reversed  - test for that
                    result.__setattr__(at, me_and_my_attribute_value - him_and_hers_attribute_value)
                except TypeError as t:
                    if type(self.__getattribute__(at)) != type(other.__getattribute__(at)):   # noqa
                        raise TypeError(f"The type of self.{at} is {type(self.__getattribute__(at))}"
                                        f"The type of other.{at} is {type(other.__getattribute__(at))}")
                    else:
                        print(f"handling an unknown type error, {str(t)}", file=sys.stderr)
                        print(f"The types are {type(self.__getattribute__(at))}, " 
                              f"{type(other.__getattribute__(at))}", file=sys.stderr)
        # This test protects against the caller doing something stupid
        assert isinstance(result.time, datetime.timedelta), f"result.time should be a datetime.timedelta, is  \
                   {type(result)}"
        return result

    def __eq__(self, other: 'Layer') -> bool:
        """

        :param other: The other object to compare against self
        :return: True if all of the fields are equal EXCEPT time, False otherwise
        """
        for at in self.__dict__:
            if at == "time":
                continue
            if self.__getattribute__(at) != other.__getattribute__(at):
                return False
        return True

    @classmethod
    def discover(cls) -> typing.Dict[str, 'Layer']:
        """
        Return a dictionary which key'd by the name of the
        object and the value is an an object of that OSI level
        This is an abstract class that all classes that import this class
        must override.
        """
        d: typing.Dict[str, 'Layer'] = {}
        if "nefarious name" not in d:
            raise NotImplementedError
        return d


    def dict_from_class(self) -> typing.Dict[str, dict]:
        """
        Converts all of the attributes of this object into a dictionary
        This is needed because JSON wants bools, ints, floats, lists or dicts
        :return:
        """
        return dict(
            (key, value) for (key, value) in self.__dict__.items()
            if not callable(value))


if "__main__" == __name__:
    TEST_DELAY = 2.0
    me: Layer = Layer("ennie")
    me.e = 4
    me.q = 17
    assert callable(me.discover), "discover is a method and should be callable"
    assert not callable(me.e), "e should NOT be callable, and it is"
    time.sleep(TEST_DELAY)
    mini_me = Layer("ennie")
    mini_me.e = 6
    mini_me.q = 6
    dup = Layer("ennie")
    dup.e = me.e
    dup.q = me.q

    it = Layer("meenie")
    who: datetime = datetime.datetime.now()

    with pytest.raises(ValueError):
        # The other object is not an instance of Layer.  This tests that if
        # the minus operator is given something that is not a Layer, it raises
        # and exception.
        q = it - who  # noqa This is supposed to be two different types

    with pytest.raises(ValueError):
        q7 = me - it

    delta: Layer = mini_me - me
    assert isinstance(delta.time, datetime.timedelta), f"delta.time should be datetime.timedelta is {type(delta.time)}"
    dt = abs(delta.time)  # abs works as expected for timedelta types
    assert dt.seconds <= TEST_DELAY * 1.02, \
        f"delta.time.seconds should be less than {TEST_DELAY * 1.02} but it's {delta.time.seconds}"

    assert delta.e == 2, f"delta.e should be 2, is actually {delta.e}"
    assert delta.q == -11, f"delta.q should be -11, is actually {delta.q}"

    assert me != mini_me, "me should be different than mini_me"
    assert me == dup, "me should be the same as mini_me"

    dict_from_layer: dict = me.dict_from_class()
    assert isinstance(dict_from_layer, dict), \
        "dict_from_layer isn't a dict, it's a {0}".format(str(type(me)))
    assert 'e' in dict_from_layer, "There should be a key, 'e', in me and there isn't"
    assert dict_from_layer['e'] == 4, f"me.e should be 4, but it really is {me['e']}"
