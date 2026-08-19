import re

import pytest
from pydantic import BaseModel, ValidationError

from mex.common.types import VOCABULARY_ENUMS, AnyVocabularyEnum, VocabularyEnum
from mex.model import VOCABULARY_JSON_BY_NAME


def concept_to_member_name(pref_label_en: str) -> str:
    """Derive the enum member name from the english prefLabel of a concept."""
    return "_".join(
        word.upper() for word in re.split("[^a-zA-Z0-9]", pref_label_en) if word
    )


def scheme_to_vocabulary_name(scheme: str) -> str:
    """Derive the vocabulary slug of a scheme url, e.g. `access-restriction`."""
    return scheme.rsplit("/", 1)[-1]


class DummyEnum(VocabularyEnum):
    """Dummy vocabulary for testing."""

    __scheme__ = "https://mex.rki.de/item/dummy-vocabulary"

    PREF_EN_ONE = "https://mex.rki.de/item/dummy-concept-1"
    PREF_EN_TWO = "https://mex.rki.de/item/dummy-concept-2"


@pytest.mark.parametrize(
    "vocabulary_enum",
    VOCABULARY_ENUMS,
    ids=[vocabulary_enum.__name__ for vocabulary_enum in VOCABULARY_ENUMS],
)
def test_hardcoded_enum_matches_mex_model(
    vocabulary_enum: type[AnyVocabularyEnum],
) -> None:
    vocabulary_name = scheme_to_vocabulary_name(vocabulary_enum.__scheme__)
    concepts = VOCABULARY_JSON_BY_NAME[vocabulary_name.replace("-", "_")]

    # check names, values and order of the hardcoded members match the vocabulary
    assert [(member.name, member.value) for member in vocabulary_enum] == [
        (concept_to_member_name(concept["prefLabel"]["en"]), concept["identifier"])
        for concept in concepts
    ]

    # check the hardcoded scheme matches the one the concepts declare
    assert {concept["inScheme"] for concept in concepts} == {vocabulary_enum.__scheme__}


def test_vocabulary_enums_cover_all_vocabularies() -> None:
    enum_vocabularies = {
        scheme_to_vocabulary_name(vocabulary_enum.__scheme__)
        for vocabulary_enum in VOCABULARY_ENUMS
    }
    all_vocabularies = {name.replace("_", "-") for name in VOCABULARY_JSON_BY_NAME}
    assert enum_vocabularies == all_vocabularies


def test_vocabulary_enum_model() -> None:
    class DummyModel(BaseModel):
        dummy: DummyEnum

    # check wrong type raises error
    with pytest.raises(ValidationError):
        DummyModel.model_validate({"dummy": object()})

    # check wrong value raises error
    with pytest.raises(ValidationError):
        DummyModel.model_validate(
            {"dummy": "https://mex.rki.de/item/not-a-valid-concept"}
        )

    # check parsing from string works
    model = DummyModel.model_validate(
        {"dummy": "https://mex.rki.de/item/dummy-concept-2"}
    )
    assert model.dummy == DummyEnum["PREF_EN_TWO"]

    # check wrong value raises error in json mode
    with pytest.raises(ValidationError):
        DummyModel.model_validate_json(
            '{"dummy": "https://mex.rki.de/item/not-a-valid-concept"}'
        )

    # check parsing from json works
    model = DummyModel.model_validate_json(
        '{"dummy": "https://mex.rki.de/item/dummy-concept-2"}'
    )
    assert model.dummy == DummyEnum["PREF_EN_TWO"]


def test_vocabulary_enum_schema() -> None:
    class DummyModel(BaseModel):
        dummy: DummyEnum

    assert DummyModel.model_json_schema() == {
        "properties": {
            "dummy": {
                "examples": ["https://mex.rki.de/item/dummy-concept-1"],
                "pattern": "https://mex.rki.de/item/[a-z0-9-]+",
                "title": "Dummy",
                "type": "string",
                "useScheme": "https://mex.rki.de/item/dummy-vocabulary",
            }
        },
        "required": ["dummy"],
        "title": "DummyModel",
        "type": "object",
    }
