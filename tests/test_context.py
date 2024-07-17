import pytest

from mex.common.context import SingleSingletonStore


class Parent:
    pass


class Child(Parent):
    pass


def test_single_singleton_store() -> None:
    store = SingleSingletonStore["Parent"]()
    parent = store.load(Parent)

    with pytest.raises(RuntimeError, match="is not a parent class of loaded class"):
        store.load(Child)

    assert parent is store.load(Parent)

    store.push(Child())

    child = store.load(Child)

    assert child is store.load(Parent)

    store.reset()

    assert store._singleton is None
