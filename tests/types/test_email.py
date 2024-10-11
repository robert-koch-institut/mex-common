import pytest
from pydantic import BaseModel, ValidationError

from mex.common.types import EMAIL_PATTERN, Email


class DummyModel(BaseModel):
    email: Email


def test_email_validation() -> None:
    model = DummyModel.model_validate({"email": "wasd@def.ghi"})
    assert model.email == Email("wasd@def.ghi")

    model = DummyModel.model_validate({"email": Email("wasd@def.ghi")})
    assert model.email == Email("wasd@def.ghi")

    model = DummyModel(email=Email("wasd@def.ghi"))
    assert model.email == Email("wasd@def.ghi")

    with pytest.raises(ValidationError):
        DummyModel.model_validate({"email": "foobar"})

    with pytest.raises(ValidationError):
        DummyModel.model_validate({"email": object()})


def test_email_serialization() -> None:
    model = DummyModel.model_validate({"email": "wasd@def.ghi"})
    raw = model.model_dump()

    assert raw == {"email": "wasd@def.ghi"}


def test_email_schema() -> None:
    assert DummyModel.model_json_schema() == {
        "properties": {
            "email": {
                "examples": ["info@rki.de"],
                "format": "email",
                "pattern": EMAIL_PATTERN,
                "title": "Email",
                "type": "string",
            }
        },
        "required": ["email"],
        "title": "DummyModel",
        "type": "object",
    }


def test_email_repr() -> None:
    assert repr(Email("wasd@def.ghi")) == 'Email("wasd@def.ghi")'
