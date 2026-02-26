import json
from datetime import timedelta, timezone
from enum import Enum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Annotated, Any
from uuid import UUID

import pytest
from pydantic import AnyUrl, Field, SecretStr
from pydantic import BaseModel as PydanticModel

from mex.common.transform import (
    MExEncoder,
    camel_to_split,
    camelcase_to_title,
    clean_dict,
    dromedary_to_kebab,
    dromedary_to_snake,
    ensure_postfix,
    ensure_prefix,
    kebab_to_camel,
    normalize,
    snake_to_dromedary,
    split_to_camel,
    split_to_caps,
    to_key_and_values,
)
from mex.common.types import Identifier, PathWrapper, TemporalEntity


class DummyModel(PydanticModel):
    string_field: Annotated[str, Field(alias="strField")] = "bar"
    integer: int = 42


class DummyEnum(Enum):
    THIS = "this"
    THAT = "that"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (DummyModel(strField="bar"), '{"integer": 42, "string_field": "bar"}'),
        (
            AnyUrl("http://example:8000/path/?query=test"),
            '"http://example:8000/path/?query=test"',
        ),
        (SecretStr("str"), '"str"'),
        (DummyEnum.THAT, '"that"'),
        (UUID(int=4, version=4), '"00000000-0000-4000-8000-000000000004"'),
        (Identifier.generate(seed=4), '"bFQoRhcVH5DHUu"'),
        (TemporalEntity(2012), '"2012"'),
        (TemporalEntity(2010, 12), '"2010-12"'),
        (TemporalEntity(2010, 12, 24), '"2010-12-24"'),
        (TemporalEntity(2010, 12, 24, 23, 59, 59), '"2010-12-24T23:41:59Z"'),
        (
            TemporalEntity(
                2010, 12, 24, 23, 59, 59, tzinfo=timezone(timedelta(hours=-2))
            ),
            '"2010-12-25T01:59:59Z"',
        ),
        (PureWindowsPath(r"C:\\System\\Win32\\exe.dll"), '"C:/System/Win32/exe.dll"'),
        (PurePosixPath(r"/dev/sys/etc/launch.ctl"), '"/dev/sys/etc/launch.ctl"'),
        (Path("relative", "path"), '"relative/path"'),
        (PathWrapper("relative/path"), '"relative/path"'),
    ],
)
def test_mex_json_encoder(raw: object, expected: str) -> None:
    assert json.dumps(raw, cls=MExEncoder, sort_keys=True) == expected


def test_mex_json_encoder_unserializable() -> None:
    with pytest.raises(TypeError, match="object is not JSON serializable"):
        assert json.dumps({"foo": object()}, cls=MExEncoder)


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", ""),
        ("word", "word"),
        ("alreadyDromedary", "alreadyDromedary"),
        ("multiple_words_in_a_string", "multipleWordsInAString"),
    ],
    ids=[
        "empty",
        "single word",
        "already dromedary",
        "multiple words",
    ],
)
def test_snake_to_dromedary(string: str, expected: str) -> None:
    result = snake_to_dromedary(string)
    assert result == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", ""),
        ("word", "word"),
        ("already_snake", "already_snake"),
        ("ABWordCDEWordFG", "ab_word_cde_word_fg"),
        ("multipleWordsInAString", "multiple_words_in_a_string"),
    ],
    ids=[
        "empty",
        "single word",
        "already snake",
        "caps words",
        "multiple words",
    ],
)
def test_dromedary_to_snake(string: str, expected: str) -> None:
    result = dromedary_to_snake(string)
    assert result == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", ""),
        ("word", "word"),
        ("already-kebab", "already-kebab"),
        ("Such-AWeird-MIXEDCase", "such-a-weird-mixed-case"),
        ("ABWordCDEWordFG", "ab-word-cde-word-fg"),
        ("multipleWordsInAString", "multiple-words-in-a-string"),
    ],
    ids=[
        "empty",
        "single word",
        "already kebab",
        "mixed case",
        "caps words",
        "multiple words",
    ],
)
def test_dromedary_to_kebab(string: str, expected: str) -> None:
    result = dromedary_to_kebab(string)
    assert result == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", ""),
        ("word", "Word"),
        ("AlreadyCamel", "AlreadyCamel"),
        ("Mixed-CASE", "MixedCase"),
        ("multiple-words-in-a-string", "MultipleWordsInAString"),
    ],
    ids=[
        "empty",
        "single word",
        "already camel",
        "mixed case",
        "multiple words",
    ],
)
def test_kebab_to_camel(string: str, expected: str) -> None:
    result = kebab_to_camel(string)
    assert result == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", ""),
        ("word", "word"),
        ("CamelCase", "Camel Case"),
        ("ABWordCDEWordFG", "AB Word CDE Word FG"),
        ("multipleWordsInAString", "multiple Words In A String"),
        ("XMLHttpRequest", "XML Http Request"),
        ("IOError", "IO Error"),
    ],
    ids=[
        "empty",
        "single word",
        "camel case",
        "caps words",
        "dromedary case",
        "mixed caps",
        "all caps acronym",
    ],
)
def test_camel_to_split(string: str, expected: str) -> None:
    result = camel_to_split(string)
    assert result == expected


@pytest.mark.parametrize(
    ("input_camelcase", "expected"),
    [
        ("", ""),
        ("simplestring", "Simplestring"),
        ("inputCamelCase", "Input Camel Case"),
        (
            "a bit_weird string_that might be _work _for_some_reason_",
            "A Bit_Weird String_That Might Be _Work _For_Some_Reason_",
        ),
    ],
    ids=["empty string", "simple string", "simple camelcase", "weird camelcase"],
)
def test_camelcase_to_title(input_camelcase: str, expected: str) -> None:
    assert camelcase_to_title(input_camelcase) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [("", ""), ("__XYZ__", "xyz"), ("/foo/BAR$42", "foo bar 42")],
)
def test_normalize(string: str, expected: str) -> None:
    assert normalize(string) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", ""),
        ("word", "Word"),
        ("CamelCase", "CamelCase"),
        ("Camel Case", "CamelCase"),
        ("AB Word CDE Word FG", "AbWordCdeWordFg"),
        ("multiple Words In A String", "MultipleWordsInAString"),
        ("XML Http Request", "XmlHttpRequest"),
        ("IO Error", "IoError"),
    ],
    ids=[
        "empty",
        "single word",
        "already camel",
        "camel case",
        "caps words",
        "dromedary case",
        "mixed caps",
        "all caps acronym",
    ],
)
def test_split_to_camel(string: str, expected: str) -> None:
    result = split_to_camel(string)
    assert result == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("", ""),
        ("Foo(Bar) 99 - Batz", "FOO_BAR_BATZ"),
    ],
)
def test_split_to_caps(string: str, expected: str) -> None:
    assert split_to_caps(string) == expected


@pytest.mark.parametrize(
    ("string", "prefix", "expected"),
    [
        ("", "", ""),
        ("banana", "ba", "banana"),
        ("bar", "foo", "foobar"),
        (
            -42,
            UUID("{12345678-1234-5678-1234-567812345678}"),
            "12345678-1234-5678-1234-567812345678-42",
        ),
    ],
    ids=["empty", "already-prefixed", "prefix-added", "stringified"],
)
def test_ensure_prefix(string: object, prefix: object, expected: str) -> None:
    result = ensure_prefix(string, prefix)

    assert result == expected


@pytest.mark.parametrize(
    ("string", "postfix", "expected"),
    [
        ("", "", ""),
        ("banana", "na", "banana"),
        ("foo", "bar", "foobar"),
        (
            UUID("{12345678-1234-5678-1234-567812345678}"),
            -42,
            "12345678-1234-5678-1234-567812345678-42",
        ),
    ],
    ids=["empty", "already-postfixed", "postfix-added", "stringified"],
)
def test_ensure_postfix(
    string: object,
    postfix: object,
    expected: str,
) -> None:
    result = ensure_postfix(string, postfix)

    assert result == expected


@pytest.mark.parametrize(
    ("dct", "expected"),
    [
        ({}, {}),
        (
            {"single": 32, "nested": {"foo": 42}, "empty": None},
            {"single": [32], "nested": [{"foo": 42}], "empty": []},
        ),
        (
            {"one": [32], "three": [32, 42, 3.1], "empty": []},
            {"one": [32], "three": [32, 42, 3.1], "empty": []},
        ),
    ],
    ids=["empty", "singles", "lists"],
)
def test_to_key_and_values(dct: dict[str, Any], expected: dict[str, list[Any]]) -> None:
    result = dict(to_key_and_values(dct))

    assert result == expected


@pytest.mark.parametrize(
    ("obj", "unwanted", "expected"),
    [
        ({}, (None, []), {}),
        ({"a": 1, "b": None, "c": []}, (None, []), {"a": 1}),
        ({"a": {"b": None, "c": 2}}, (None, []), {"a": {"c": 2}}),
        ({"a": [1, {"b": None, "c": 3}]}, (None, []), {"a": [1, {"c": 3}]}),
        ("plain", (None, []), "plain"),
        (42, (None, []), 42),
        ({"a": 0, "b": "", "c": False}, (None, []), {"a": 0, "b": "", "c": False}),
        ({"a": 1, "b": 0}, (None, [], 0), {"a": 1}),
    ],
    ids=[
        "empty dict",
        "removes None and empty list",
        "nested dict",
        "list with nested dict",
        "non-dict passthrough string",
        "non-dict passthrough int",
        "keeps falsy non-unwanted values",
        "custom unwanted",
    ],
)
def test_clean_dict(obj: Any, unwanted: tuple[Any, ...], expected: Any) -> None:  # noqa: ANN401
    assert clean_dict(obj, unwanted) == expected
