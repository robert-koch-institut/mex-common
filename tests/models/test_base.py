from enum import Enum
from typing import Any, Optional, Union

import pytest

from mex.common.models import BaseModel
from mex.common.models.base import FlatValueMap
from mex.common.types import Timestamp


class Animal(Enum):
    """Dummy enum to use in tests."""

    CAT = "cat"
    DOG = "dog"


@pytest.mark.parametrize(
    "mapping, expected",
    [
        ({}, "N/A"),
        ({"key": None}, "N/A"),
        ({"key": Timestamp(1970, 1, 1)}, "1970-01-01"),
        ({"key": ["foo", 0.1, Animal.CAT]}, "foo, 0.1, cat"),
    ],
    ids=[
        "missing key",
        "missing value",
        "single value",
        "list value",
    ],
)
def test_flat_value_map(mapping: dict[str, Any], expected: str) -> None:
    flat_value_map = FlatValueMap(mapping)
    assert flat_value_map["key"] == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        ({"optional_str": []}, {"optional_str": None}),
        ({"optional_str": [None]}, {"optional_str": None}),
        ({"optional_str": ["value"]}, {"optional_str": "value"}),
        (
            {"required_str": []},
            "Input should be a valid string [type=string_type, input_value=None, "
            "input_type=NoneType]",
        ),
        (
            {"required_str": [None]},
            "Input should be a valid string [type=string_type, input_value=None, "
            "input_type=NoneType]",
        ),
        (
            {"required_str": ["value", "value"]},
            "got multiple values for required_str [type=value_error, "
            "input_value={'required_str': ['value', 'value']}, input_type=dict]",
        ),
        ({"optional_list": None}, {"optional_list": None}),
        ({"optional_list": "value"}, {"optional_list": ["value"]}),
        ({"required_list": None}, {"required_list": []}),
        ({"required_list": "value"}, {"required_list": ["value"]}),
    ],
)
def test_base_model_listyness_fix(
    data: dict[str, Any], expected: Union[str, dict[str, Any]]
) -> None:
    class ListynessFixModel(BaseModel):
        optional_str: Optional[str] = None
        required_str: str = "default"
        optional_list: Optional[list[str]] = None
        required_list: list[str] = []

    try:
        model = ListynessFixModel.model_validate(data)
    except Exception as error:
        assert str(expected) in str(error)
    else:
        assert model.model_dump(exclude_unset=True) == expected


class DummyModel(BaseModel):
    foo: Optional[str] = None


def test_checksum() -> None:
    model_1 = DummyModel()
    assert model_1.checksum() == "9a3cba5e4d465e234420e2ffd04135dc"

    model_2 = DummyModel(foo="bar")
    assert model_1.checksum() != model_2.checksum()


def test_model_str() -> None:
    model = DummyModel(foo="bar")
    assert str(model) == "DummyModel: cd6a532d2c8c8a90f378f7af53db351b"
