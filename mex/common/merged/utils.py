import contextlib
from typing import TypeVar

_ListItemT = TypeVar("_ListItemT")


def extend_list_in_dict(
    dict_: dict[str, list[_ListItemT]],
    key: str,
    item: list[_ListItemT] | _ListItemT | None,
) -> None:
    """Extend a list in a dict for a given key with the given unique item(s)."""
    list_ = dict_.setdefault(key, [])
    if item is None:
        item = []
    elif not isinstance(item, list):
        item = [item]
    for mergeable in item:
        if mergeable not in list_:
            list_.append(mergeable)


def prune_list_in_dict(
    dict_: dict[str, list[_ListItemT]],
    key: str,
    item: list[_ListItemT] | _ListItemT | None,
) -> None:
    """Safely remove item(s) from a list in a dict for the given key."""
    list_ = dict_.setdefault(key, [])
    if item is None:
        item = []
    elif not isinstance(item, list):
        item = [item]
    for removable in item:
        with contextlib.suppress(ValueError):
            list_.remove(removable)
