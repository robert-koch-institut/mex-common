import platform
import re
from pathlib import Path

import pytest

from mex.common.settings import BaseSettings, SettingsContext
from mex.common.types import AssetsPath, WorkPath


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
    assert re.search(r"backend_api_key\s+\*+", text)  # masked secret


class FooSettings(BaseSettings):
    """Dummy settings subclass for testing."""

    foo: str = "foo"


class BarSettings(BaseSettings):
    """Second dummy settings subclass for testing."""

    bar: str = "bar"


def test_settings_getting_caches_singleton() -> None:
    # clear cache
    SettingsContext.set({})  # clear cache

    # first get
    settings = FooSettings.get()
    cached_settings = SettingsContext.get().get(FooSettings)
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


def test_resolve_paths() -> None:
    class DummySettings(BaseSettings):
        non_path: str
        abs_path: WorkPath
        work_path: WorkPath
        assets_path: AssetsPath

    if platform.system() == "Windows":  # pragma: no cover
        absolute = WorkPath(r"C:\absolute\path")
    else:  # pragma: no cover
        absolute = WorkPath("/absolute/path")
    relative = Path("relative", "path")

    settings = DummySettings(
        non_path="blablabla",
        abs_path=absolute,
        work_path=WorkPath(relative),
        assets_path=AssetsPath(relative),
        assets_dir=Path(absolute / "assets_dir"),
    )

    settings_dict = settings.model_dump(exclude_defaults=True)
    assert settings_dict["non_path"] == "blablabla"
    assert settings_dict["abs_path"] == absolute
    assert settings_dict["work_path"] == WorkPath(settings.work_dir / relative)
    assert settings_dict["assets_path"] == AssetsPath(
        absolute / "assets_dir" / relative
    )
