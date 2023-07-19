import json

import pytest
from click.testing import CliRunner

from mex.common.models import ExtractedResource
from mex.common.models.access_platform import TechnicalAccessibility
from mex.common.scripts.schema import SchemaScriptsSettings, dump_schema


@pytest.fixture(autouse=True)
def settings() -> SchemaScriptsSettings:
    """Load the settings for this pytest session."""
    return SchemaScriptsSettings.get()


def test_dump_schema_script() -> None:
    runner = CliRunner()
    settings = SchemaScriptsSettings.get()

    result = runner.invoke(dump_schema, env=settings.env())
    assert result.exit_code == 0, result.stdout

    with open(settings.json_file) as fh:
        schema = json.load(fh)

    assert schema["title"] == settings.schema_title
    assert TechnicalAccessibility.__name__ in schema["definitions"]
    assert ExtractedResource.__name__ in schema["definitions"]
