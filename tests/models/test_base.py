from enum import Enum
from typing import Annotated, Any, Literal

import pytest
from pydantic import Field, ValidationError

from mex.common.models import BaseModel, MergedItem
from mex.common.types import Identifier


class ComplexDummyModel(BaseModel):
    """Dummy Model with multiple attributes."""

    optional_str: str | None = None
    required_str: str = "default"
    optional_list: list[str] | None = None
    required_list: list[str] = []


def test_get_field_names_allowing_none() -> None:
    assert ComplexDummyModel._get_field_names_allowing_none() == [
        "optional_str",
        "optional_list",
    ]


def test_get_list_field_names() -> None:
    assert ComplexDummyModel._get_list_field_names() == [
        "optional_list",
        "required_list",
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
    data: dict[str, Any], expected: str | dict[str, Any]
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


class DummyBaseModel(BaseModel):
    foo: str | None = None


def test_base_model_checksum() -> None:
    model_1 = DummyBaseModel()
    assert model_1.checksum() == "da8e081aa63fd2fd5b909dd86c6dfa6c"

    model_2 = DummyBaseModel(foo="bar")
    assert model_1.checksum() != model_2.checksum()


def test_base_model_str() -> None:
    model = DummyBaseModel(foo="bar")
    assert str(model) == "DummyBaseModel: 94232c5b8fc9272f6f73a1e36eb68fcf"
