import json
from datetime import timedelta, timezone
from enum import Enum
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from uuid import UUID

import pytest
from pydantic import BaseModel as PydanticModel
from pydantic import Field, SecretStr

from mex.common.transform import (
    MExEncoder,
    dromedary_to_kebab,
    dromedary_to_snake,
    kebab_to_camel,
    snake_to_dromedary,
)
from mex.common.types import Identifier, Timestamp


class DummyModel(PydanticModel):
    string_field: str = Field("foo", alias="strField")
    integer: int = 42


class DummyEnum(Enum):
    THIS = "this"
    THAT = "that"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (DummyModel(strField="bar"), '{"integer": 42, "string_field": "bar"}'),
        (SecretStr("str"), '"str"'),
        (DummyEnum.THAT, '"that"'),
        (UUID(int=4, version=4), '"00000000-0000-4000-8000-000000000004"'),
        (Identifier.generate(seed=4), '"bFQoRhcVH5DHUu"'),
        (Timestamp(2012), '"2012"'),
        (Timestamp(2010, 12), '"2010-12"'),
        (Timestamp(2010, 12, 24), '"2010-12-24"'),
        (Timestamp(2010, 12, 24, 23, 59, 59), '"2010-12-24T22:59:59Z"'),
        (
            Timestamp(2010, 12, 24, 23, 59, 59, tzinfo=timezone(timedelta(hours=-2))),
            '"2010-12-25T01:59:59Z"',
        ),
        (PureWindowsPath(r"C:\\System\\Win32\\exe.dll"), '"C:/System/Win32/exe.dll"'),
        (PurePosixPath(r"/dev/sys/etc/launch.ctl"), '"/dev/sys/etc/launch.ctl"'),
        (Path("relative", "path"), '"relative/path"'),
    ],
)
def test_mex_json_encoder(raw: Any, expected: str) -> None:
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
        ("ABWordCDEWordFG", "ab-word-cde-word-fg"),
        ("multipleWordsInAString", "multiple-words-in-a-string"),
    ],
    ids=[
        "empty",
        "single word",
        "already kebab",
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
        ("word", "word"),
        ("alreadyCamel", "alreadyCamel"),
        ("multiple-words-in-a-string", "multipleWordsInAString"),
    ],
    ids=[
        "empty",
        "single word",
        "already camel",
        "multiple words",
    ],
)
def test_kebab_to_camel(string: str, expected: str) -> None:
    result = kebab_to_camel(string)
    assert result == expected
