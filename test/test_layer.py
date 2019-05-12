#! /usr/bin/exec python3
# _*_ coding: utf-8 _*_


# test layer.py
# The methods to test are:
"""
    def __init__(self, name: str) -> None:
    def get_status(self) -> constants.ErrorLevels:
    def __sub__(self, other: 'Layer') -> 'Layer':
    def __eq__(self, other: 'Layer') -> bool:
    def discover(cls) -> typing.Dict[str, 'Layer']:
    def dict_from_class(self) -> typing.Dict[str, dict]:
"""

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
        # This should raise a ValueError exception because me has two
        # attributes, e and q, that are not in it.
        q7 = me - it

    delta: Layer = mini_me - me
    # The time attribute is the time when the object was instantiated
    assert isinstance(delta.time, datetime.timedelta), f"delta.time should be datetime.timedelta is {type(delta.time)}"
    dt = abs(delta.time)  # abs works as expected for timedelta types
    # I am allowing a 2% error in the time.sleep call, that might be too small
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
