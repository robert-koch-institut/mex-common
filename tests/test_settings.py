import os
import platform
import re
from pathlib import Path
from typing import Annotated

import pytest
from pydantic import Field

from mex.common.settings import BaseSettings, SettingsContext


def test_debug_setting() -> None:
    # Test settings can be instantiated as basic sanity check
    settings = BaseSettings(debug=True)  # type: ignore

    assert settings.debug is True


def test_settings_text() -> None:
    # Test settings can be converted to a legible multi-line paragraph
    settings = BaseSettings.get()
    text = settings.text()

    assert len(text.splitlines()) == len(BaseSettings.model_fields)
    assert re.search(r"debug\s+False", text)
    assert re.search(r"api_token_payload\s+\*+", text)  # masked secret


def test_settings_env_keys() -> None:
    settings = BaseSettings.get()
    keys = settings.env_keys()

    assert len(keys) == len(settings.model_fields)
    assert "MEX_DEBUG" in keys


class FooSettings(BaseSettings):
    """Dummy settings subclass for testing."""

    foo: str = "foo"


class BarSettings(BaseSettings):
    """Second dummy settings subclass for testing."""

    bar: str = "bar"


def test_settings_getting_caches_singleton() -> None:
    # clear cache
    SettingsContext.set(None)  # clear cache

    # first get
    settings = FooSettings.get()
    cached_settings = SettingsContext.get()
    assert settings is cached_settings

    # repeated get
    settings_fetched_again = FooSettings.get()
    assert settings_fetched_again is settings


@pytest.mark.integration
def test_parse_env_file() -> None:
    settings = BaseSettings.get()
    # "work_dir" and "assets_dir" are always set, assert that more than these two are
    # set. This indicates an .env file was found and at least one setting was parsed.
    assert settings.model_fields_set != {"work_dir", "assets_dir"}


def test_settings_getting_wrong_class_raises_error() -> None:
    # first get foo settings
    FooSettings.get()
    assert isinstance(SettingsContext.get(), FooSettings)

    # then try to get another, non-related settings class
    with pytest.raises(RuntimeError, match="already loaded"):
        BarSettings.get()


def test_resolve_paths() -> None:
    class DummySettings(BaseSettings):
        non_path: str
        abs_path: Annotated[Path, Field(json_schema_extra={"path_type": "WorkPath"})]
        work_path: Annotated[Path, Field(json_schema_extra={"path_type": "WorkPath"})]
        assets_path: Annotated[
            Path, Field(json_schema_extra={"path_type": "AssetsPath"})
        ]

    if platform.system() == "Windows":  # pragma: no cover
        absolute = Path(r"C:\absolute\path")
    else:
        absolute = Path("/absolute/path")
    relative = Path("relative", "path")

    settings = DummySettings(
        non_path="blablabla",
        abs_path=absolute,
        work_path=relative,
        assets_path=relative,
        assets_dir=os.path.join(absolute, "assets_dir"),
    )

    settings_dir = settings.model_dump(exclude_defaults=True)
    assert settings_dir["non_path"] == "blablabla"
    assert settings_dir["abs_path"] == absolute
    assert settings.work_path == settings.work_dir / relative
    assert settings_dir["assets_path"] == Path(
        os.path.join(absolute, "assets_dir", relative)
    )
