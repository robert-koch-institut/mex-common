import logging
import re
from enum import Enum
from typing import Any, Union

import pytest
from click.testing import CliRunner
from pydantic import HttpUrl
from pydantic.fields import FieldInfo, ModelField
from pytest import LogCaptureFixture

from mex.common.cli import _field_to_option, entrypoint
from mex.common.settings import BaseSettings


class MyStr(str):
    """Dummy string subclass for _field_to_option test."""


class MyEnum(Enum):
    """Dummy enum class for _field_to_option test."""

    FOO = 1
    BAR = 2


@pytest.mark.parametrize(
    ("field", "info_dict"),
    [
        (
            ModelField(
                name="required_field",
                class_validators={},
                default=4.2,
                model_config=BaseSettings.__config__,
                required=True,
                type_=float,
            ),
            {
                "name": "required_field",
                "param_type_name": "option",
                "opts": ["--required-field"],
                "secondary_opts": [],
                "type": {"param_type": "Float", "name": "float"},
                "required": False,
                "nargs": 1,
                "multiple": False,
                "default": 4.2,
                "envvar": "MEX_REQUIRED_FIELD",
                "help": None,
                "prompt": None,
                "is_flag": False,
                "flag_value": False,
                "count": False,
                "hidden": False,
            },
        ),
        (
            ModelField(
                name="url_field",
                class_validators={},
                default="https://example.com",
                model_config=BaseSettings.__config__,
                type_=HttpUrl,
            ),
            {
                "name": "url_field",
                "param_type_name": "option",
                "opts": ["--url-field"],
                "secondary_opts": [],
                "type": {"param_type": "String", "name": "text"},
                "required": False,
                "nargs": 1,
                "multiple": False,
                "default": "https://example.com",
                "envvar": "MEX_URL_FIELD",
                "help": None,
                "prompt": None,
                "is_flag": False,
                "flag_value": False,
                "count": False,
                "hidden": False,
            },
        ),
        (
            ModelField(
                name="str_like_field",
                class_validators={},
                default=MyStr("test"),
                model_config=BaseSettings.__config__,
                type_=MyStr,
            ),
            {
                "name": "str_like_field",
                "param_type_name": "option",
                "opts": ["--str-like-field"],
                "secondary_opts": [],
                "type": {"param_type": "String", "name": "text"},
                "required": False,
                "nargs": 1,
                "multiple": False,
                "default": "test",
                "envvar": "MEX_STR_LIKE_FIELD",
                "help": None,
                "prompt": None,
                "is_flag": False,
                "flag_value": False,
                "count": False,
                "hidden": False,
            },
        ),
        (
            ModelField(
                name="optional_flag",
                class_validators={},
                default=False,
                field_info=FieldInfo(description="This flag is optional"),
                model_config=BaseSettings.__config__,
                type_=bool,
            ),
            {
                "name": "optional_flag",
                "param_type_name": "option",
                "opts": ["--optional-flag"],
                "secondary_opts": [],
                "type": {"param_type": "Bool", "name": "boolean"},
                "required": False,
                "nargs": 1,
                "multiple": False,
                "default": False,
                "envvar": "MEX_OPTIONAL_FLAG",
                "help": "This flag is optional",
                "prompt": None,
                "is_flag": True,
                "flag_value": True,
                "count": False,
                "hidden": False,
            },
        ),
        (
            ModelField(
                name="enum_list",
                class_validators={},
                default=[MyEnum.FOO, MyEnum.BAR],
                field_info=FieldInfo(description="Multiple values allowed"),
                model_config=BaseSettings.__config__,
                type_=list[MyEnum],
            ),
            {
                "name": "enum_list",
                "param_type_name": "option",
                "opts": ["--enum-list"],
                "secondary_opts": [],
                "type": {"name": "text", "param_type": "String"},
                "required": False,
                "nargs": 1,
                "multiple": False,  # on purpose, because we let pydantic parse lists
                "default": "[1, 2]",
                "envvar": "MEX_ENUM_LIST",
                "help": "Multiple values allowed",
                "prompt": None,
                "is_flag": False,
                "flag_value": False,
                "count": False,
                "hidden": False,
            },
        ),
        (
            ModelField(
                name="union_field",
                class_validators={},
                default=True,
                field_info=FieldInfo(description="String or boolean"),
                model_config=BaseSettings.__config__,
                type_=Union[bool, str],  # type: ignore
            ),
            {
                "name": "union_field",
                "param_type_name": "option",
                "opts": ["--union-field"],
                "secondary_opts": [],
                "type": {"name": "text", "param_type": "String"},
                "required": False,
                "nargs": 1,
                "multiple": False,
                "default": "true",
                "envvar": "MEX_UNION_FIELD",
                "help": "String or boolean",
                "prompt": None,
                "is_flag": False,
                "flag_value": False,
                "count": False,
                "hidden": False,
            },
        ),
    ],
    ids=[
        "required field",
        "url field",
        "str-like field",
        "optional flag",
        "enum list",
        "union field",
    ],
)
def test_field_to_option(field: ModelField, info_dict: dict[str, Any]) -> None:
    option = _field_to_option(field)
    assert option.to_info_dict() == info_dict


def test_good_entrypoint_exits_zero() -> None:
    @entrypoint(BaseSettings)
    def good_entrypoint() -> None:
        return

    result = CliRunner().invoke(good_entrypoint, args=[])
    assert result.exit_code == 0, result.stdout


def test_faulty_entrypoint_exits_non_zero() -> None:
    @entrypoint(BaseSettings)
    def faulty_entrypoint() -> None:
        1 / 0

    result = CliRunner().invoke(faulty_entrypoint, args=[])
    assert result.exit_code == 1, result.stdout


def test_entrypoint_logs_docs_and_settings(caplog: LogCaptureFixture) -> None:
    class ChattySettings(BaseSettings):
        custom_setting: str = "default"

    @entrypoint(ChattySettings)
    def chatty_entrypoint() -> None:
        """Hi, I am Pointy McEntryFace."""
        return

    with caplog.at_level(logging.INFO, logger="mex"):
        result = CliRunner().invoke(
            chatty_entrypoint, args=["--custom-setting=override"]
        )
    assert result.exit_code == 0, result.stdout

    assert "Pointy McEntryFace" in caplog.text
    assert re.search(r"custom_setting\s+override", caplog.text)
