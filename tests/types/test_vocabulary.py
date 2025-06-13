import json

import pytest
from pydantic import BaseModel, ValidationError
from pytest import MonkeyPatch

from mex.common.types import VocabularyEnum
from mex.model import VOCABULARY_JSON_BY_NAME
from tests.types.conftest import TESTDATA_DIR


@pytest.fixture
def use_dummy_vocabulary(monkeypatch: MonkeyPatch) -> None:
    with (TESTDATA_DIR / "dummy-vocabulary.json").open() as fh:
        dummy_vocabulary = json.load(fh)
    monkeypatch.setitem(VOCABULARY_JSON_BY_NAME, "dummy_vocabulary", dummy_vocabulary)


@pytest.mark.usefixtures("use_dummy_vocabulary")
def test_vocabulary_enum_model() -> None:
    class DummyEnum(VocabularyEnum):
        __vocabulary__ = "dummy-vocabulary"

    # check enum names are loaded correctly
    assert [c.name for c in DummyEnum] == ["PREF_EN_ONE", "PREF_EN_TWO"]

    # check enum values are loaded correctly
    assert [c.value for c in DummyEnum] == [
        "https://mex.rki.de/item/dummy-concept-1",
        "https://mex.rki.de/item/dummy-concept-2",
    ]

    # check enum instance representation
    assert repr(DummyEnum["PREF_EN_ONE"]) == 'DummyEnum["PREF_EN_ONE"]'

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


@pytest.mark.usefixtures("use_dummy_vocabulary")
def test_vocabulary_enum_schema() -> None:
    class DummyEnum(VocabularyEnum):
        __vocabulary__ = "dummy-vocabulary"

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


@pytest.mark.usefixtures("use_dummy_vocabulary")
def test_vocabulary_enum_find() -> None:
    class DummyEnum(VocabularyEnum):
        __vocabulary__ = "dummy-vocabulary"

    assert len(DummyEnum.__concepts__) == 2
    assert DummyEnum.find("not-found") is None

    found_enum = DummyEnum.find("pref-de-one")
    assert found_enum is not None
    assert found_enum.value == "https://mex.rki.de/item/dummy-concept-1"
