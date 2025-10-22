from typing import TypeVar

from networkx import DiGraph, NetworkXUnfeasible
from networkx import topological_sort as network_sort

from mex.common.exceptions import MExError
from mex.common.utils import ensure_list

ItemT = TypeVar("ItemT")


def topological_sort(
    items: list[ItemT],
    primary_key: str,
    *,
    parent_key: str | None = None,
    child_key: str | None = None,
) -> None:
    """Sort the given list of items in-place according to their topology.

    Items can refer to each other using key fields. A parent item can reference a child
    item by storing the child's `primary_key` in the parent's `child_key` field.
    Similarly, a child can reference its parent using the `parent_key` field.

    This can be useful for submitting items to the backend in the correct order.
    """
    graph: DiGraph[str] = DiGraph()
    for item in items:
        current_node = getattr(item, primary_key)
        graph.add_node(current_node)
        if parent_key:
            for parent_node in ensure_list(getattr(item, parent_key)):
                graph.add_edge(parent_node, current_node)
        if child_key:
            for child_node in ensure_list(getattr(item, child_key)):
                graph.add_edge(current_node, child_node)

    try:
        sorted_keys = list(network_sort(graph))
    except NetworkXUnfeasible as error:
        msg = "Found graph cycles while sorting."
        raise MExError(msg) from error

    items.sort(
        key=lambda item: (
            sorted_keys.index(getattr(item, primary_key)),
            getattr(item, primary_key),
        )
    )
