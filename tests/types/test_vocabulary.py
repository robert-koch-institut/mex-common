import pytest
from pydantic import BaseModel, ValidationError
from pytest import MonkeyPatch

from mex.common.types import Vocabulary, VocabularyEnum, split_to_caps
from tests.types.conftest import TESTDATA_DIR


@pytest.mark.parametrize(
    "string, expected",
    [
        ("", ""),
        ("Foo(Bar) 99 - Batz", "FOO_BAR_BATZ"),
    ],
)
def test_split_to_caps(string: str, expected: str) -> None:
    assert split_to_caps(string) == expected


@pytest.fixture
def use_dummy_vocabulary(monkeypatch: MonkeyPatch) -> None:
    dummy_vocabulary = Vocabulary.parse_file(TESTDATA_DIR / "dummy-vocabulary.json")
    monkeypatch.setattr(Vocabulary, "parse_file", lambda *_: dummy_vocabulary)


@pytest.mark.usefixtures("use_dummy_vocabulary")
def test_vocabulary_enum_model() -> None:
    class DummyEnum(VocabularyEnum):
        __vocabulary__ = "dummy-vocabulary"

    # check enum names are loaded correctly
    assert [c.name for c in DummyEnum] == ["PREF_EN_ONE", "PREF_EN_TWO"]

    # check enum values are loaded correctly
    assert [c.value for c in DummyEnum] == [
        "https://dummy/concept-one",
        "https://dummy/concept-two",
    ]

    # check enum instance representation
    assert repr(DummyEnum["PREF_EN_ONE"]) == 'DummyEnum["PREF_EN_ONE"]'

    class DummyModel(BaseModel):
        dummy: DummyEnum

    # check wrong type raises error
    with pytest.raises(ValidationError):
        DummyModel.parse_obj({"dummy": object()})

    # check wrong value raises error
    with pytest.raises(ValidationError):
        DummyModel.parse_obj({"dummy": "https://dummy/not-a-valid-concept"})

    # check parsing from string works
    model = DummyModel.parse_obj({"dummy": "https://dummy/concept-two"})
    assert model.dummy == DummyEnum["PREF_EN_TWO"]


@pytest.mark.usefixtures("use_dummy_vocabulary")
def test_vocabulary_enum_find() -> None:
    class DummyEnum(VocabularyEnum):
        __vocabulary__ = "dummy-vocabulary"

    assert len(DummyEnum.__concepts__) == 2
    assert DummyEnum.find("not-found") is None

    found_enum = DummyEnum.find("pref-de-one")
    assert found_enum is not None
    assert found_enum.value == "https://dummy/concept-one"
