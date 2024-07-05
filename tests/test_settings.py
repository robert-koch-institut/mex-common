import platform
import re
from pathlib import Path

import pytest

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
    SETTINGS_STORE.reset()

    # first get
    settings = FooSettings.get()
    cached_settings = SETTINGS_STORE.load(FooSettings)
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

    class SubModel(BaseModel):
        sub_model_path: WorkPath

    class DummySettings(BaseSettings):
        non_path: str
        abs_work_path: WorkPath
        rel_work_path: WorkPath
        assets_path: AssetsPath
        sub_model: SubModel

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

    settings_dict = DummySettings.get().model_dump(exclude_defaults=True)
    assert settings_dict["non_path"] == "blablabla"
    assert settings_dict["abs_work_path"] == absolute
    assert settings_dict["rel_work_path"] == WorkPath(settings.work_dir / relative)
    assert settings_dict["assets_path"] == AssetsPath(
        absolute / "assets_dir" / relative
    )
    assert settings_dict["sub_model"]["sub_model_path"] == WorkPath(
        settings.work_dir / relative
    )


class BlueSettings(BaseSettings):
    color: str = "blue"


class RedSettings(BaseSettings):
    color: str = "red"


def test_sync_settings_from_base(tmp_path: Path) -> None:
    # GIVEN an instance of the base settings and a subclass
    base_settings = BaseSettings.get()
    blue_settings = BlueSettings.get()

    # GIVEN a field that belongs to the `BaseSettings` scope
    assert "work_dir" in BaseSettings.model_fields

    # GIVEN the two settings start out with the same `work_dir`
    assert base_settings.work_dir == blue_settings.work_dir

    # WHEN we change the `work_dir` on the `BaseSetting`
    base_settings.work_dir = tmp_path / "base-update"

    # THEN the changes should be synced to new `BlueSettings`
    blue_settings = BlueSettings.get()
    assert blue_settings.work_dir == tmp_path / "base-update"


def test_sync_settings_from_subclasses(tmp_path: Path) -> None:
    # GIVEN an instance of the base settings and two subclasses
    base_settings = BaseSettings.get()
    blue_settings = BlueSettings.get()
    red_settings = RedSettings.get()

    # GIVEN all settings start out with the same `work_dir`
    assert base_settings.work_dir == blue_settings.work_dir == red_settings.work_dir

    # WHEN we change the `work_dir` on the `BlueSetting`
    blue_settings.work_dir = tmp_path / "blue-update"

    # THEN the changes should be synced to new `BaseSettings` and `RedSettings`
    base_settings = BaseSettings.get()
    red_settings = RedSettings.get()
    assert blue_settings.work_dir == tmp_path / "blue-update"
    assert red_settings.work_dir == tmp_path / "blue-update"
