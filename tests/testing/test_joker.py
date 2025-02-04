from mex.common.testing import Joker


def test_joker_eq() -> None:
    assert Joker() == None  # noqa: E711
    assert Joker() == 1
    assert {"foo": Joker()} == {"foo": ["bar", Joker()]}


def test_joker_repr() -> None:
    joker = Joker()
    assert {"question": joker} == {"question": "Why so serious?"}
    assert repr(joker) == "'Why so serious?'"
