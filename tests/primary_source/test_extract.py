from mex.common.primary_source.extract import extract_seed_primary_sources
from mex.common.types import TextLanguage


def test_extract_seed_primary_sources() -> None:
    seed_primary_source = list(extract_seed_primary_sources())

    assert len(seed_primary_source) == 5
    assert seed_primary_source[0].model_dump() == {
        "identifier": "mex",
        "title": [{"value": "Metadata Exchange", "language": TextLanguage.EN}],
    }
