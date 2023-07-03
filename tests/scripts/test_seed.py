import pytest
from click.testing import CliRunner

from mex.common.scripts.seed import SeedScriptSettings, insert_primary_sources_into_db


@pytest.fixture(autouse=True)
def settings() -> SeedScriptSettings:
    """Load the settings for this pytest session."""
    return SeedScriptSettings.get()


def test_insert_primary_sources_into_db() -> None:
    settings = SeedScriptSettings.get()
    result = CliRunner().invoke(insert_primary_sources_into_db, env=settings.env())

    assert result.exit_code == 0, result.stdout
