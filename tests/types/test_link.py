import pytest
from pydantic import BaseModel, ValidationError

from mex.common.types import Link, LinkLanguage


class DummyModel(BaseModel):
    link: Link


def test_link_validation() -> None:
    with pytest.raises(ValidationError, match="Allowed input types are dict and str"):
        _ = DummyModel.model_validate({"link": 1})

    model = DummyModel.model_validate({"link": "https://example.com"})
    assert model.model_dump() == {
        "link": {
            "language": None,
            "title": None,
            "url": "https://example.com",
        }
    }

    model = DummyModel.model_validate(
        {"link": {"url": "https://example.com", "title": "Example", "language": "en"}}
    )
    assert model.model_dump() == {
        "link": {
            "language": LinkLanguage.EN,
            "title": "Example",
            "url": "https://example.com",
        }
    }


def test_link_hash() -> None:
    link = Link(url="https://foo.bar", title="Hallo Welt.", language=LinkLanguage.DE)
    assert hash(link) == hash(("https://foo.bar", "Hallo Welt.", LinkLanguage.DE))
