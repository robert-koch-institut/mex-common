from mex.common.models import MergedItem
from mex.common.types import Identifier


def test_merged_item_get_entity_type() -> None:
    assert MergedItem.get_entity_type() == "MergedItem"


def test_merged_item_str() -> None:
    item = MergedItem(identifier=Identifier.generate(seed=99))
    assert str(item) == "MergedItem: bFQoRhcVH5DHV1"
