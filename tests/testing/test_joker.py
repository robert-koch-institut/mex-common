from mex.common.testing import Joker


def test_joker_eq() -> None:
    assert Joker() == None
    assert Joker() == 1
    assert {"foo": Joker()} == {"foo": ["bar", Joker()]}


def test_joker_repr() -> None:
    joker = Joker()
    assert {"question": "Why so serious?"} == {"question": joker}
    assert repr(joker) == "'Why so serious?'"
