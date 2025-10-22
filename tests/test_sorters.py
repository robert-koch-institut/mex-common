from dataclasses import dataclass

import pytest

from mex.common.exceptions import MExError
from mex.common.sorters import topological_sort


@dataclass
class Item:
    id: str
    parent: list[str] | str | None = None
    child: list[str] | str | None = None


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (
            [
                Item(id="ChildB", parent="Parent"),
                Item(id="GrandParent"),
                Item(id="ChildA", parent="Parent"),
                Item(id="Parent", parent="GrandParent"),
            ],
            [
                Item(id="GrandParent"),
                Item(id="Parent", parent="GrandParent"),
                Item(id="ChildB", parent="Parent"),
                Item(id="ChildA", parent="Parent"),
            ],
        ),
        (
            [
                Item(id="ChildB", parent=["ParentA", "ParentB"]),
                Item(id="ParentB"),
                Item(id="ChildC", parent="ParentA"),
                Item(id="ParentA"),
                Item(id="ChildA", parent=["ParentB", "ParentA"]),
            ],
            [
                Item(id="ParentA"),
                Item(id="ParentB"),
                Item(id="ChildC", parent="ParentA"),
                Item(id="ChildB", parent=["ParentA", "ParentB"]),
                Item(id="ChildA", parent=["ParentB", "ParentA"]),
            ],
        ),
        (
            [
                Item(id="ChildB"),
                Item(id="ParentB", child=["ChildB"]),
                Item(id="ChildC", parent="ParentA"),
                Item(id="ParentA", child=["ChildB", "ChildA"]),
                Item(id="ChildA", parent=["ParentB", "ParentA"]),
            ],
            [
                Item(id="ParentB", child=["ChildB"]),
                Item(id="ParentA", child=["ChildB", "ChildA"]),
                Item(id="ChildC", parent="ParentA"),
                Item(id="ChildB"),
                Item(id="ChildA", parent=["ParentB", "ParentA"]),
            ],
        ),
    ],
    ids=["single parent", "multi parents", "two way"],
)
def test_topological_sort(items: list[Item], expected: list[Item]) -> None:
    topological_sort(items, "id", parent_key="parent", child_key="child")
    assert items == expected


def test_topological_sort_circular_error() -> None:
    items = [
        Item(id="North", child=["East"]),
        Item(id="East", child=["South"]),
        Item(id="South", child=["West"]),
        Item(id="West", child=["North"]),
    ]
    with pytest.raises(MExError, match=r"Found graph cycles while sorting"):
        topological_sort(items, "id", child_key="child")
