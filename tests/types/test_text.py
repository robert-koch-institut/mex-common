import pytest
from pydantic import BaseModel, ValidationError

from mex.common.types import Text, TextLanguage


def test_text_language_detect() -> None:
    # accepted languages are only German, English, French, Spanish and Russian for now
    de_text = Text(value="Diese tiefen Seufzern haben einen Sinn. Legt sie uns aus.")
    assert de_text.language == TextLanguage.DE
    en_text = Text(value="There's matter in these sighs. You must translate.")
    assert en_text.language == TextLanguage.EN
    fr_text = Text(value="Ces profonds soupirs ont un sens. Expliquez-les-nous.")
    assert fr_text.language == TextLanguage.FR
    es_text = Text(
        value="Estos profundos suspiros tienen un significado. Tradúcelos para nosotros."
    )
    assert es_text.language == TextLanguage.ES
    ru_text = Text(value="Эти глубокие вздохи имеют смысл. Объясните их нам.")
    assert ru_text.language == TextLanguage.RU

    # language that can be detected by langdetect but should be excluded from results
    ko_text = Text(value="이 한숨에는 문제가 있습니다. 번역해야 합니다.")
    assert ko_text.language is None

    # language that langdetect does not know and should not be included in results
    am_text = Text(value="በእነዚህ ቅስቀሳዎች ውስጥ ቁም ነገር አለ። መተርጎም አለብዎት.")
    assert am_text.language is None

    # check that we can overwrite the language
    overwrite_text = Text(
        value="There's matter in these sighs. You must translate",
        language=TextLanguage.DE,
    )
    assert overwrite_text.language == TextLanguage.DE

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
        "text": {"value": "we are parsing a string here", "language": TextLanguage.EN}
    }

    model = DummyModel.model_validate(
        {"text": {"value": "and here, we are parsing an object"}}
    )
    assert model.model_dump() == {
        "text": {
            "value": "and here, we are parsing an object",
            "language": TextLanguage.EN,
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
            "language": TextLanguage.DE,
        }
    }


def test_text_hash() -> None:
    text = Text(value="Hallo Welt.", language=TextLanguage.DE)
    assert hash(text) == hash(("Hallo Welt.", TextLanguage.DE))
