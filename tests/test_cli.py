import logging
import re
from enum import Enum
from typing import Any

import pytest
from click.testing import CliRunner
from pydantic import HttpUrl, create_model
from pydantic.fields import Field
from pytest import LogCaptureFixture

from mex.common.cli import _field_to_option, entrypoint
from mex.common.settings import BaseSettings


class MyStr(str):
    """Dummy string subclass for _field_to_option test."""

    __slots__ = ()


class MyEnum(Enum):
    """Dummy enum class for _field_to_option test."""

    FOO = 1
    BAR = 2


@pytest.mark.parametrize(
    ("name", "settings_cls", "info_dict"),
    [
        (
            "required_field",
            create_model(
                "RequiredFieldSettings",
                __base__=BaseSettings,
                required_field=(float, Field()),
            ),
            {
                "name": "required_field",
                "param_type_name": "option",
                "opts": ["--required-field"],
                "secondary_opts": [],
                "type": {"param_type": "Float", "name": "float"},
                "required": True,
                "nargs": 1,
                "multiple": False,
                "default": None,
                "envvar": "MEX_REQUIRED_FIELD",
                "help": None,
                "prompt": None,
                "is_flag": False,
                "flag_value": None,
                "count": False,
                "hidden": False,
            },
        ),
        (
            "url_field",
            create_model(
                "UrlFieldSettings",
                __base__=BaseSettings,
                url_field=(HttpUrl, "https://example.com"),
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
                "flag_value": None,
                "count": False,
                "hidden": False,
            },
        ),
        (
            "str_like_field",
            create_model(
                "StrLikeFieldSettings",
                __base__=BaseSettings,
                str_like_field=(MyStr, MyStr("test")),
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
                "flag_value": None,
                "count": False,
                "hidden": False,
            },
        ),
        (
            "optional_flag",
            create_model(
                "OptionalFlagSettings",
                __base__=BaseSettings,
                optional_flag=(
                    bool,
                    Field(default=False, description="This flag is optional"),
                ),
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
            "enum_list",
            create_model(
                "EnumListSettings",
                __base__=BaseSettings,
                enum_list=(
                    list[MyEnum],
                    Field(
                        [MyEnum.FOO, MyEnum.BAR], description="Multiple values allowed"
                    ),
                ),
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
                "flag_value": None,
                "count": False,
                "hidden": False,
            },
        ),
        (
            "union_field",
            create_model(
                "UnionFieldSettings",
                __base__=BaseSettings,
                union_field=(
                    bool | str,
                    Field(default=True, description="String or boolean"),
                ),
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
                "flag_value": None,
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
def test_field_to_option(
    name: str, settings_cls: type[BaseSettings], info_dict: dict[str, Any]
) -> None:
    option = _field_to_option(name, settings_cls)
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
        _ = 1 / 0

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
