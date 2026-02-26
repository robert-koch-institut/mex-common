import platform
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from mex.common.models import BaseModel
from mex.common.settings import SETTINGS_STORE, BaseSettings
from mex.common.types import AssetsPath, WorkPath


def test_debug_setting() -> None:
    # Test settings can be instantiated as basic sanity check
    settings = BaseSettings(debug=True)

    assert settings.debug is True


def test_settings_text() -> None:
    # Test settings can be converted to a legible multi-line paragraph
    settings = BaseSettings.get()
    settings.debug = True
    text = settings.text()

    assert all(field in text for field in BaseSettings.model_fields)
    assert re.findall(r".*debug.*True.*", text)
    assert re.search(r".*backend_api_key.*\*{10}", text)  # masked secret


class FooSettings(BaseSettings):
    """Dummy settings subclass for testing."""

    foo: str = "foo"


class BarSettings(BaseSettings):
    """Second dummy settings subclass for testing."""

    bar: str = "bar"


class BazSettings(BaseSettings):
    """Third dummy settings subclass for testing."""

    foo: BaseSettings = FooSettings()


def test_settings_getting_caches_singleton() -> None:
    # clear cache
    SETTINGS_STORE.reset()

    # first get
    settings = FooSettings.get()
    cached_settings = SETTINGS_STORE.load(FooSettings)
    assert settings is cached_settings

    # repeated get
    settings_fetched_again = FooSettings.get()
    assert settings_fetched_again is settings


class SubModel(BaseModel):
    sub_model_path: WorkPath


class DummySettings(BaseSettings):
    non_path: str
    abs_work_path: WorkPath
    rel_work_path: WorkPath
    assets_path: AssetsPath
    sub_model: SubModel


def test_resolve_paths() -> None:
    if platform.system() == "Windows":  # pragma: no cover
        absolute = WorkPath(r"C:\absolute\path")
    else:  # pragma: no cover
        absolute = WorkPath("/absolute/path")

    relative = WorkPath(Path("relative", "path"))

    settings = DummySettings(
        non_path="blablabla",
        abs_work_path=absolute,
        rel_work_path=relative,
        assets_path=AssetsPath(relative),
        assets_dir=Path(absolute / "assets_dir"),
        work_dir=Path(absolute / "work_dir"),
        sub_model=SubModel(sub_model_path=relative),
    )

    assert settings.non_path == "blablabla"
    assert settings.abs_work_path == absolute
    assert settings.rel_work_path == WorkPath(settings.work_dir / relative)
    assert settings.assets_path == AssetsPath(absolute / "assets_dir" / relative)
    assert settings.sub_model.sub_model_path == WorkPath(settings.work_dir / relative)


def test_no_settings_as_attributes() -> None:
    # regular settings instantiation passes
    FooSettings()

    # setting with attribute that inherits from BaseSettings fails
    with pytest.raises(ValidationError):
        BazSettings()
