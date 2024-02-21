from enum import Enum
from typing import Annotated, Any, Literal, Optional, Union

import pytest
from pydantic import Field, ValidationError

from mex.common.models import BaseModel, MergedItem
from mex.common.types import Identifier


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


class DummyBaseModel(BaseModel):
    foo: Optional[str] = None


def test_base_model_checksum() -> None:
    model_1 = DummyBaseModel()
    assert model_1.checksum() == "69d67f58c6948849283e78d7b3f1a51e"

    model_2 = DummyBaseModel(foo="bar")
    assert model_1.checksum() != model_2.checksum()


def test_base_model_str() -> None:
    model = DummyBaseModel(foo="bar")
    assert str(model) == "DummyBaseModel: ab794a793aad8fa45b0f85ac05ee2126"


def test_mex_model_str() -> None:
    class MergedDummy(MergedItem):
        entityType: Annotated[
            Literal["MergedDummy"], Field(alias="$type", frozen=True)
        ] = "MergedDummy"
        identifier: Identifier

    model = MergedDummy(identifier=Identifier.generate(seed=99))

    assert str(model) == "MergedDummy: bFQoRhcVH5DHV1"
