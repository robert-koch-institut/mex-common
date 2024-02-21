from enum import Enum
from typing import Any, Optional, Union

import pytest
from pydantic import ValidationError

from mex.common.models import BaseModel


class ComplexDummyModel(BaseModel):
    """Dummy Model with multiple attributes."""

    optional_str: Optional[str] = None
    required_str: str = "default"
    optional_list: Optional[list[str]] = None
    required_list: list[str] = []


def test_get_field_names_allowing_none() -> None:
    assert ComplexDummyModel._get_field_names_allowing_none() == [
        "optional_str",
        "optional_list",
    ]


class Animal(Enum):
    """Dummy enum to use in tests."""

    CAT = "cat"
    DOG = "dog"


@pytest.mark.parametrize(
    ("data", "expected"),
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
    try:
        model = ComplexDummyModel.model_validate(data)
    except Exception as error:
        assert str(expected) in str(error)
    else:
        assert model.model_dump(exclude_unset=True) == expected


def test_base_model_listyness_fix_only_runs_on_mutable_mapping() -> None:
    class Pet(BaseModel):
        name: str

    class Shelter(Pet):
        inhabitants: list[Pet]

    # make sure this raises a validation error and does not fail in fix_listyness
    with pytest.raises(
        ValidationError, match="Input should be a valid dictionary or instance of Pet"
    ):
        Shelter(inhabitants="foo")  # type: ignore


class DummyModel(BaseModel):
    foo: Optional[str] = None


def test_checksum() -> None:
    model_1 = DummyModel()
    assert model_1.checksum() == "6a48475b6851bc444c39abec23f8520e"

    model_2 = DummyModel(foo="bar")
    assert model_1.checksum() != model_2.checksum()


def test_model_str() -> None:
    model = DummyModel(foo="bar")
    assert str(model) == "DummyModel: 68008f92758ef95dd4de3319183c3fef"
