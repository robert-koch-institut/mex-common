import pytest
from pydantic import BaseModel, ValidationError

from mex.common.types import Link, LinkLanguage


def test_parsing_from_string() -> None:
    class DummyModel(BaseModel):
        link: Link

    # plain link
    model = DummyModel.model_validate({"link": "https://example.com"})
    assert model.model_dump(exclude_none=True) == {
        "link": {"url": "https://example.com"}
    }

    # link with title
    model = DummyModel.model_validate({"link": "[Example](https://example.com)"})
    assert model.model_dump(exclude_none=True) == {
        "link": {"url": "https://example.com", "title": "Example"}
    }

    # link with funky characters
    model = DummyModel.model_validate(
        {"link": r"[\[TEST\] Example](https://example.com/test?q=\(\.\*\))"}
    )
    assert model.model_dump(exclude_none=True) == {
        "link": {"url": "https://example.com/test?q=(.*)", "title": "[TEST] Example"}
    }

    # nested model
    model = DummyModel.model_validate(
        {"link": {"url": "https://example.com", "title": "Example", "language": "en"}}
    )
    assert model.model_dump(exclude_none=True) == {
        "link": {
            "url": "https://example.com",
            "title": "Example",
            "language": LinkLanguage.EN,
        }
    }

    # invalid data
    with pytest.raises(ValidationError):
        DummyModel.model_validate(["lists", "are", "not", "valid"])


def test_rendering_as_string() -> None:
    # plain link
    link = Link.model_validate({"url": "https://example.com"})
    assert str(link) == "https://example.com"

    # link with title
    link = Link.model_validate({"url": "https://example.com", "title": "Example"})
    assert str(link) == r"[Example](https://example\.com)"

    # link with funky characters
    link = Link.model_validate(
        {"url": "https://example.com/test?q=(.*)", "title": "[TEST] Example"}
    )
    assert str(link) == r"[\[TEST\] Example](https://example\.com/test?q=\(\.\*\))"
