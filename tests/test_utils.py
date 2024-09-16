import json
import time
from collections.abc import Iterable
from types import NoneType
from typing import Annotated, Any, Literal

import pytest
from pydantic.fields import FieldInfo

from mex.common.models import BaseModel
from mex.common.types import (
    MERGED_IDENTIFIER_CLASSES,
    Identifier,
    MergedPersonIdentifier,
)
from mex.common.utils import (
    any_contains_any,
    contains_any,
    contains_only_types,
    get_inner_types,
    group_fields_by_class_name,
    grouper,
    jitter_sleep,
    normalize,
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
def test_contains_any(base: Any, tokens: Iterable[Any], expected: bool) -> None:
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
def test_any_contains_any(base: Any, tokens: Iterable[Any], expected: bool) -> None:
    assert any_contains_any(base, tokens) == expected


@pytest.mark.parametrize(
    ("annotation", "types", "expected"),
    (
        (None, [str], False),
        (str, [str], True),
        (str, [Identifier], False),
        (Identifier, [str], False),
        (list[str | int | list[str]], [str, float], False),
        (list[str | int | list[str]], [int, str], True),
        (MergedPersonIdentifier | None, MERGED_IDENTIFIER_CLASSES, True),
    ),
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
    annotation: Any, types: list[type], expected: bool
) -> None:
    class DummyModel(BaseModel):
        attribute: annotation

    assert contains_only_types(DummyModel.model_fields["attribute"], *types) == expected


@pytest.mark.parametrize(
    ("annotation", "flags", "expected_types"),
    (
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
        (Literal["okay"] | None, {}, [Literal, NoneType]),
        (
            Literal["okay"] | None,
            {"unpack_literal": False},
            [Literal["okay"], NoneType],
        ),
    ),
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
        "annotated string or int",
        "unpacking literal",
        "not unpacking literal",
    ],
)
def test_get_inner_types(
    annotation: Any, flags: dict[str, bool], expected_types: list[type]
) -> None:
    assert list(get_inner_types(annotation, **flags)) == expected_types


def test_group_fields_by_class_name() -> None:
    class DummyModel(BaseModel):
        number: int
        text: str

    class PseudoModel(BaseModel):
        title: str

    lookup = {"Dummy": DummyModel, "Pseudo": PseudoModel}
    expected = {"Dummy": ["text"], "Pseudo": ["title"]}
    assert group_fields_by_class_name(lookup, lambda f: f.annotation is str) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    (("", ""), ("__XYZ__", "xyz"), ("/foo/BAR$42", "foo bar 42")),
)
def test_normalize(string: str, expected: str) -> None:
    assert normalize(string) == expected


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
