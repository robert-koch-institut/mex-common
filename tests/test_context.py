import pytest

from mex.common.context import SingleSingletonStore, SingletonStore


class Parent:
    pass


class Child(Parent):
    pass


def test_singleton_store() -> None:
    store = SingletonStore["Parent"]()
    parent = store.load(Parent)

    popped = store.pop(Parent)
    assert popped is parent

    new_parent = store.load(Parent)
    assert new_parent is not parent

    store.reset()

    assert not store._instances_by_class


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
