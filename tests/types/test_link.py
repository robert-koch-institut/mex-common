from pydantic import BaseModel

from mex.common.types import Link, LinkLanguage


def test_parsing_from_string() -> None:
    class DummyModel(BaseModel):
        link: Link

    # plain link
    model = DummyModel.parse_obj({"link": "https://example.com"})
    assert model.dict(exclude_none=True) == {"link": {"url": "https://example.com"}}

    # link with title
    model = DummyModel.parse_obj({"link": "[Example](https://example.com)"})
    assert model.dict(exclude_none=True) == {
        "link": {"url": "https://example.com", "title": "Example"}
    }

    # link with funky characters
    model = DummyModel.parse_obj(
        {"link": r"[\[TEST\] Example](https://example.com/test?q=\(\.\*\))"}
    )
    assert model.dict(exclude_none=True) == {
        "link": {"url": "https://example.com/test?q=(.*)", "title": "[TEST] Example"}
    }

    # nested model
    model = DummyModel.parse_obj(
        {"link": {"url": "https://example.com", "title": "Example", "language": "en"}}
    )
    assert model.dict(exclude_none=True) == {
        "link": {
            "url": "https://example.com",
            "title": "Example",
            "language": LinkLanguage.EN,
        }
    }


def test_rendering_as_string() -> None:
    # plain link
    link = Link.parse_obj({"url": "https://example.com"})
    assert str(link) == "https://example.com"

    # link with title
    link = Link.parse_obj({"url": "https://example.com", "title": "Example"})
    assert str(link) == r"[Example](https://example\.com)"

    # link with funky characters
    link = Link.parse_obj(
        {"url": "https://example.com/test?q=(.*)", "title": "[TEST] Example"}
    )
    assert str(link) == r"[\[TEST\] Example](https://example\.com/test?q=\(\.\*\))"
