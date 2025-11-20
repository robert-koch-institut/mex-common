import pytest
from pydantic import BaseModel, ValidationError

from mex.common.types import Text
from mex.common.types.text import RestrictedTextLanguage, get_language_confidence


def test_text_language_detect() -> None:
    # accepted languages are only German and English. Other languages are None.
    de_text = Text(value="Diese tiefen Seufzern haben einen Sinn. Legt sie uns aus.")
    assert de_text.language == RestrictedTextLanguage.DE
    en_text = Text(value="There's matter in these sighs. You must translate.")
    assert en_text.language == RestrictedTextLanguage.EN

    # language that can be detected by langdetect but should be excluded from results
    fr_text = Text(value="Ces profonds soupirs ont un sens. Expliquez-les-nous.")
    assert fr_text.language is None
    es_text = Text(
        value="Estos profundos suspiros tienen un significado. Tradúcelos para nosotros."
    )
    assert es_text.language is None
    ru_text = Text(value="Эти глубокие вздохи имеют смысл. Объясните их нам.")
    assert ru_text.language is None
    ko_text = Text(value="이 한숨에는 문제가 있습니다. 번역해야 합니다.")
    assert ko_text.language is None

    # language that langdetect does not know and should not be included in results
    am_text = Text(value="በእነዚህ ቅስቀሳዎች ውስጥ ቁም ነገር አለ። መተርጎም አለብዎት.")
    assert am_text.language is None

    # check that we can overwrite the language
    overwrite_text = Text(
        value="There's matter in these sighs. You must translate",
        language=RestrictedTextLanguage.DE,
    )
    assert overwrite_text.language == RestrictedTextLanguage.DE

    # check that we can explicitly null the language
    none_text = Text(
        value="There's matter in these sighs. You must translate", language=None
    )
    assert none_text.language is None


class DummyModel(BaseModel):
    text: Text


def test_text_validation() -> None:
    with pytest.raises(ValidationError, match="Allowed input types are dict and str"):
        _ = DummyModel.model_validate({"text": 1})

    model = DummyModel.model_validate({"text": "we are parsing a string here"})
    assert model.model_dump() == {
        "text": {
            "value": "we are parsing a string here",
            "language": RestrictedTextLanguage.EN,
        }
    }

    model = DummyModel.model_validate(
        {"text": {"value": "and here, we are parsing an object"}}
    )
    assert model.model_dump() == {
        "text": {
            "value": "and here, we are parsing an object",
            "language": RestrictedTextLanguage.EN,
        }
    }

    model = DummyModel.model_validate(
        {
            "text": {
                "value": "now we parse an object with a language key",
                "language": "de",
            }
        }
    )
    assert model.model_dump() == {
        "text": {
            "value": "now we parse an object with a language key",
            "language": RestrictedTextLanguage.DE,
        }
    }


def test_text_hash() -> None:
    text = Text(value="Hallo Welt.", language=RestrictedTextLanguage.DE)
    assert hash(text) == hash(("Hallo Welt.", RestrictedTextLanguage.DE))


class Prob:
    def __init__(self, lang: str, prob: float) -> None:
        self.lang = lang
        self.prob = prob


class MockedDetector:
    def __init__(self, probs: list[Prob]) -> None:
        self._probs = probs

    def get_probabilities(self) -> list[Prob]:
        return self._probs


@pytest.mark.parametrize(
    ("probs", "expected"),
    [
        ([Prob("en", 0.95)], RestrictedTextLanguage.EN),
        ([Prob("de", 0.88)], RestrictedTextLanguage.DE),
        ([Prob("fr", 0.92)], None),
        ([Prob("en", 0.40)], None),
        (
            [Prob("de", 0.40), Prob("en", 0.20), Prob("de", 0.80)],
            RestrictedTextLanguage.DE,
        ),
        ([], None),
    ],
    ids=[
        "high_confidence_en",
        "high_confidence_de",
        "fr_unsupported_none",
        "low_confidence_en_none",
        "highest_prob_selected_de",
        "no_language_detected_none",
    ],
)
def test_get_language_confidence(
    probs: list[Prob],
    expected: RestrictedTextLanguage | None,
) -> None:
    detector = MockedDetector(probs)
    result = get_language_confidence(detector)
    assert result == expected
