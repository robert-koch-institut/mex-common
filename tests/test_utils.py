import json
import time
from collections.abc import Iterable
from types import NoneType
from typing import Annotated, Any, Literal

import pytest
from pydantic import computed_field
from pydantic.fields import FieldInfo

from mex.common.models import BaseModel
from mex.common.types import (
    MERGED_IDENTIFIER_CLASSES,
    Identifier,
    MergedPersonIdentifier,
)
from mex.common.utils import (
    GenericFieldInfo,
    any_contains_any,
    contains_any,
    contains_any_types,
    contains_only_types,
    ensure_list,
    get_alias_lookup,
    get_all_fields,
    get_field_names_allowing_none,
    get_inner_types,
    get_list_field_names,
    group_fields_by_class_name,
    grouper,
    jitter_sleep,
)


@pytest.mark.parametrize(
    ("base", "tokens", "expected"),
    [
        ("foo", (), False),
        ("i have foo in it", ("foo", "bar", "batz"), True),
        ("i have none of the tokens ", ("foo", "bar", "batz"), False),
        ((1, 2, 3), (0, 2, 4), True),
    ],
    ids=["empty", "hit", "miss", "numbers"],
)
def test_contains_any(
    base: Any,  # noqa: ANN401
    tokens: Iterable[Any],
    expected: bool,  # noqa: FBT001
) -> None:
    assert contains_any(base, tokens) == expected


@pytest.mark.parametrize(
    ("base", "tokens", "expected"),
    [
        (["foo", None], (), False),
        (["i have foo in it", "i dont"], ("foo", "bar", "batz"), True),
        (["i have none of the tokens", "me neither"], ("foo", "bar", "batz"), False),
        (json.loads("[null, [1, 2], [], [3]]"), (0, 2, 4), True),
    ],
    ids=["empty", "hit", "miss", "numbers"],
)
def test_any_contains_any(
    base: Any,  # noqa: ANN401
    tokens: Iterable[Any],
    expected: bool,  # noqa: FBT001
) -> None:
    assert any_contains_any(base, tokens) == expected


@pytest.mark.parametrize(
    ("annotation", "types", "expected"),
    [
        (None, [str], False),
        (str, [str], True),
        (str, [Identifier], False),
        (Identifier, [str], False),
        (list[str | int | list[str]], [str, float], False),
        (list[str | int | list[str]], [int, str], True),
        (MergedPersonIdentifier | None, MERGED_IDENTIFIER_CLASSES, True),
    ],
    ids=[
        "static None",
        "simple str",
        "str vs identifier",
        "identifier vs str",
        "complex miss",
        "complex hit",
        "optional identifier",
    ],
)
def test_contains_only_types(
    annotation: Any,  # noqa: ANN401
    types: list[type],
    expected: bool,  # noqa: FBT001
) -> None:
    class DummyModel(BaseModel):
        attribute: annotation

    field_info = get_all_fields(DummyModel)["attribute"]
    assert contains_only_types(field_info, *types) == expected


@pytest.mark.parametrize(
    ("annotation", "types", "expected"),
    [
        (None, [str], False),
        (str, [str], True),
        (str, [Identifier], False),
        (Identifier, [str], False),
        (str, [int, str], True),
        (str, [int, float], False),
        (str | int, [str], True),
        (str | int, [int], True),
        (str | int, [float], False),
        (str | None, [str], True),
        (str | None, [NoneType], False),  # NoneType excluded by include_none=False
        (list[str], [str], True),
        (list[str], [list], False),  # list is unpacked by default
        (list[str | int], [str], True),
        (list[str | int], [int], True),
        (list[str | int], [float], False),
        (Annotated[str, "description"], [str], True),
        (Annotated[str | int, "description"], [str], True),
        (Annotated[str | int, "description"], [float], False),
        (Literal["value"], [Literal], True),
        (MergedPersonIdentifier | None, MERGED_IDENTIFIER_CLASSES, True),
        (MergedPersonIdentifier, MERGED_IDENTIFIER_CLASSES, True),
    ],
    ids=[
        "static None",
        "simple str match",
        "str vs identifier mismatch",
        "identifier vs str mismatch",
        "str in multiple types",
        "str not in multiple types",
        "union match first",
        "union match second",
        "union no match",
        "optional str match",
        "optional str excludes NoneType",
        "list of str",
        "list unpacked excludes list type",
        "nested union match first",
        "nested union match second",
        "nested union no match",
        "annotated str",
        "annotated union match",
        "annotated union no match",
        "literal type",
        "optional identifier match",
        "identifier match",
    ],
)
def test_contains_any_types(
    annotation: Any,  # noqa: ANN401
    types: list[type],
    expected: bool,  # noqa: FBT001
) -> None:
    field_info = GenericFieldInfo(alias=None, annotation=annotation, frozen=False)
    assert contains_any_types(field_info, *types) == expected


@pytest.mark.parametrize(
    ("annotation", "flags", "expected_types"),
    [
        (str, {}, [str]),
        (None, {}, [NoneType]),
        (None, {"include_none": False}, []),
        (str | None, {}, [str, NoneType]),
        (str | None, {"include_none": False}, [str]),
        (list[str] | None, {}, [str, NoneType]),
        (list[str | None], {}, [str, NoneType]),
        (list[int], {"unpack_list": False}, [list]),
        (list[str | int | list[str]], {}, [str, int, str]),
        (Annotated[str | int, FieldInfo(description="str or int")], {}, [str, int]),
        (Annotated[str | int, "This is a string or integer"], {}, [str, int]),
        (Literal["okay"] | None, {}, [Literal, NoneType]),
        (
            Literal["okay"] | None,
            {"unpack_literal": False},
            [Literal["okay"], NoneType],
        ),
    ],
    ids=[
        "string",
        "None allowing None",
        "None skipping None",
        "optional string allowing None",
        "optional string skipping None",
        "optional list of strings",
        "list of optional strings",
        "not unpacking list",
        "list nested in list",
        "annotated string or int with FieldInfo",
        "annotated string or int with plain text",
        "unpacking literal",
        "not unpacking literal",
    ],
)
def test_get_inner_types(
    annotation: Any,  # noqa: ANN401
    flags: dict[str, bool],
    expected_types: list[type],
) -> None:
    assert list(get_inner_types(annotation, **flags)) == expected_types


class Computer(BaseModel):
    ram: int = 16

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cpus(self) -> int:
        return 42


def test_get_all_fields_on_model_with_computed_field() -> None:
    assert get_all_fields(Computer) == {
        "cpus": GenericFieldInfo(alias=None, annotation=int, frozen=True),
        "ram": GenericFieldInfo(alias=None, annotation=int, frozen=False),
    }


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


def test_get_alias_lookup() -> None:
    assert get_alias_lookup(ComplexDummyModel) == {
        "optional_str": "optional_str",
        "required_str": "required_str",
        "optional_list": "optional_list",
        "required_list": "required_list",
        "computedInt": "computed_int",
    }


def test_get_list_field_names() -> None:
    assert get_list_field_names(ComplexDummyModel) == [
        "optional_list",
        "required_list",
    ]


def test_get_field_names_allowing_none() -> None:
    assert get_field_names_allowing_none(ComplexDummyModel) == [
        "optional_str",
        "optional_list",
    ]


def test_group_fields_by_class_name() -> None:
    class DummyModel(BaseModel):
        number: int
        text: str

    class PseudoModel(BaseModel):
        title: str

    lookup: dict[str, type[BaseModel]] = {"Dummy": DummyModel, "Pseudo": PseudoModel}
    expected = {"Dummy": ["text"], "Pseudo": ["title"]}
    assert group_fields_by_class_name(lookup, lambda f: f.annotation is str) == expected


def test_grouper() -> None:
    groups = grouper(4, "ABCDEFGHIJ")
    joined = ["".join(c or "-" for c in g) for g in groups]
    assert joined == ["ABCD", "EFGH", "IJ--"]


def test_jitter_sleep() -> None:
    t0 = time.monotonic()
    jitter_sleep(0.1, 0.2)
    t1 = time.monotonic()
    time_slept = t1 - t0

    assert 0.1 < time_slept < 0.3  # giving 100ms of courtesy to pytest


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (None, []),
        ([], []),
        ([1, 2, 3], [1, 2, 3]),
        ("single_string", ["single_string"]),
        (42, [42]),
        (True, [True]),
        ({"key": "value"}, [{"key": "value"}]),
        ([None], [None]),
        (["nested", ["list"]], ["nested", ["list"]]),
    ],
    ids=[
        "none_to_empty_list",
        "empty_list_unchanged",
        "list_unchanged",
        "string_to_list",
        "number_to_list",
        "boolean_to_list",
        "dict_to_list",
        "list_with_none_unchanged",
        "nested_list_unchanged",
    ],
)
def test_ensure_list(values: Any, expected: list[Any]) -> None:  # noqa: ANN401
    assert ensure_list(values) == expected
