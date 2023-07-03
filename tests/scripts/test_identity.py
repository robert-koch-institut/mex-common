import pandas as pd
import pytest
from click.testing import CliRunner

from mex.common.models.extracted_data import ExtractedData
from mex.common.scripts.identity import (
    IdentityScriptsSettings,
    export_identities,
    import_identities,
)
from mex.common.testing import Joker
from mex.common.types import Identifier


@pytest.fixture(autouse=True)
def settings() -> IdentityScriptsSettings:
    """Load the settings for this pytest session."""
    return IdentityScriptsSettings.get()


def test_identity_scripts_roundtrip() -> None:
    runner = CliRunner()
    settings = IdentityScriptsSettings.get()
    primary_source_id = Identifier.generate(seed=400)

    # create two extracted data instances
    ed_0_A = ExtractedData(
        hadPrimarySource=primary_source_id, identifierInPrimarySource="0"
    )
    ed_1_A = ExtractedData(
        hadPrimarySource=primary_source_id, identifierInPrimarySource="1"
    )
    assert ed_0_A.identifier != ed_1_A.identifier
    assert ed_0_A.stableTargetId != ed_1_A.stableTargetId

    # export db to file
    result = runner.invoke(export_identities, env=settings.env())
    assert result.exit_code == 0, result.stdout

    # validate written CSV
    df = pd.read_csv(settings.csv_file, dtype=str)
    assert df.to_dict("records") == [
        {
            "fragment_id": str(ed_0_A.identifier),
            "merged_id": str(ed_0_A.stableTargetId),
            "platform_id": str(primary_source_id),
            "original_id": "0",
            "entity_type": ExtractedData.get_entity_type(),
            "annotation": Joker(),
        },
        {
            "fragment_id": str(ed_1_A.identifier),
            "merged_id": str(ed_1_A.stableTargetId),
            "platform_id": str(primary_source_id),
            "original_id": "1",
            "entity_type": ExtractedData.get_entity_type(),
            "annotation": Joker(),
        },
    ]

    # set same merged ID for both
    df["merged_id"] = str(ed_0_A.stableTargetId)
    df.to_csv(settings.csv_file, lineterminator="\n")

    # import indentities back into db
    result = runner.invoke(import_identities, env=settings.env())
    assert result.exit_code == 0, result.stdout

    # recreate both extracted data instances
    ed_0_B = ExtractedData(
        hadPrimarySource=primary_source_id, identifierInPrimarySource="0"
    )
    ed_1_B = ExtractedData(
        hadPrimarySource=primary_source_id, identifierInPrimarySource="1"
    )

    # check identifiers have remained stable per extracted data
    assert ed_0_A.identifier == ed_0_B.identifier
    assert ed_1_A.identifier == ed_1_B.identifier
    assert ed_0_B.identifier != ed_1_B.identifier

    # check extracted data instance "one" has same merged_id as "nil"
    assert ed_0_B.stableTargetId == ed_1_B.stableTargetId
