import logging
from io import StringIO
from pathlib import Path

import pytest
from pytest import LogCaptureFixture, MonkeyPatch

from mex.ops.mapping.validate import _get_schema_path_from_handle, validate_mappings


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        (
            "# yaml-language-server: $schema=../../shoobidoo.json\n",
            "../../shoobidoo.json",
        ),
        (
            "asd\n# yaml-language-server: $schema=schema/not/in/first/line.json\n",
            "schema/not/in/first/line.json",
        ),
        ("blablabla", None),
    ],
)
def test_get_schema_path_from_file(body: str, expected: str | None) -> None:
    schema_path = _get_schema_path_from_handle(StringIO(body))
    assert schema_path == expected


def test_validate_mappings(monkeypatch: MonkeyPatch, caplog: LogCaptureFixture) -> None:
    valid_mapping = Path(__file__).parent / "test_data" / "valid_mapping.yaml"
    monkeypatch.setattr("sys.argv", ["test", str(valid_mapping)])
    with pytest.raises(SystemExit) as error:
        validate_mappings()
    assert error.value.code == 0

    invalid_mapping = Path(__file__).parent / "test_data" / "invalid_mapping.yaml"
    monkeypatch.setattr("sys.argv", ["test", str(invalid_mapping)])
    with pytest.raises(SystemExit) as error, caplog.at_level(
        logging.INFO, logger="mex"
    ):
        validate_mappings()
    assert error.value.code == 1
    assert "$.foo: 1 is not of type 'string'" in caplog.text
