import pytest

from mex.common.assets.filesystem import FilesystemAssetsConnector
from mex.common.settings import BaseSettings


def test_filesystem_read() -> None:
    connector = FilesystemAssetsConnector.get()

    returned = connector.read("raw-data/organigram/organizational_units.json")
    assert "Unterabteilung" in returned.decode("utf-8")


def test_glob() -> None:
    connector = FilesystemAssetsConnector.get()
    returned = connector.glob("raw-data/organigram", "*.*")
    assert returned[0].endswith("organizational_units.json")


def test_connector_only_allows_existing_path() -> None:
    connector = FilesystemAssetsConnector.get()

    with pytest.raises(
        PermissionError, match="given path is not valid or not in assets directory"
    ):
        connector._resolve_path_and_check_permission("this/path/does/not/exist.txt")


def test_connector_only_allows_sub_path(settings: BaseSettings) -> None:
    connector = FilesystemAssetsConnector.get()
    existing_file_outside_assets = "../pyproject.toml"

    assert (settings.assets_dir / existing_file_outside_assets).exists()
    with pytest.raises(
        PermissionError, match="given path is not valid or not in assets directory"
    ):
        connector._resolve_path_and_check_permission(existing_file_outside_assets)
