from typing import Any

import pytest
from pydantic import ValidationError, computed_field

from mex.common.models import BaseModel


class ComplexDummyModel(BaseModel):
    """Dummy Model with multiple attributes."""

    optional_str: str | None = None
    required_str: str = "default"
    optional_list: list[str] | None = None
    required_list: list[str] = []

    @computed_field(alias="computedInt")  # type: ignore[prop-decorator]
    @property
    def computed_int(self) -> int:
        return 42


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
        ({"computed_int": 42}, {"computed_int": 42}),
        ({"computed_int": [42]}, {"computed_int": 42}),
        (
            {"computed_int": 9999999},
            "Cannot set computed fields to custom values! [type=value_error, "
            "input_value={}, input_type=dict]",
        ),
    ],
    ids=[
        "empty list as optional single",
        "None in list as optional single",
        "string in list as optional single",
        "empty list as required single",
        "None in list as required single",
        "strings in list as required single",
        "None as optional list",
        "string as optional list",
        "None as required list",
        "string as required list",
        "correct int as computed single",
        "correct int in list as computed single",
        "false int as computed single",
    ],
)
def test_base_model_listyness_fix(
    data: dict[str, Any], expected: str | dict[str, Any]
) -> None:
    try:
        model = ComplexDummyModel.model_validate(data)
    except Exception as error:  # noqa: BLE001
        assert str(expected) in str(error)  # noqa: PT017
    else:
        actual = model.model_dump()
        assert isinstance(expected, dict)
        for key, value in expected.items():
            assert actual[key] == value


def test_base_model_listyness_fix_only_runs_on_mutable_mapping() -> None:
    class Pet(BaseModel):
        name: str

    class Shelter(Pet):
        inhabitants: list[Pet]

    # make sure this raises a validation error and does not fail in fix_listyness
    with pytest.raises(
        ValidationError, match="Input should be a valid dictionary or instance of Pet"
    ):
        Shelter(inhabitants="foo")  # type: ignore[call-arg]


class Computer(BaseModel):
    ram: int = 16

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cpus(self) -> int:
        return 42


def test_verify_computed_field_consistency() -> None:
    computer = Computer.model_validate({"cpus": 42})
    assert computer.cpus == 42

    with pytest.raises(
        ValidationError,
        match="Input should be a valid dictionary, validating other types is not "
        "supported for models with computed fields.",
    ):
        Computer.model_validate('{"cpus": 1}')

    with pytest.raises(ValidationError, match="Cannot set computed fields"):
        Computer.model_validate({"cpus": 1})

    with pytest.raises(ValidationError, match="Cannot set computed fields"):
        Computer(cpus=99)


def test_field_assignment_on_model_with_computed_field() -> None:
    computer = Computer()

    # computed field cannot be set
    with pytest.raises(
        AttributeError, match="property 'cpus' of 'Computer' object has no setter"
    ):
        computer.cpus = 99  # type: ignore[misc]

    # non-computed field works as expected
    computer.ram = 32


class DummyBaseModel(BaseModel):
    foo: str | None = None


def test_base_model_str() -> None:
    model = DummyBaseModel(foo="bar")
    assert str(model) == "DummyBaseModel(hash='0xf824b9416780b5f')"


def test_base_model_hash() -> None:
    thing1 = DummyBaseModel(foo="4567")
    thing2 = DummyBaseModel(foo="4567")
    thing3 = DummyBaseModel(foo="5678")

    assert hash(thing1) == 2305511607198672667
    assert hash(thing1) == hash(thing2)
    assert hash(thing1) != hash(thing3)
