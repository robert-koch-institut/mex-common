import pytest
from pydantic import BaseModel, ValidationError

from mex.common.types import Email


class DummyModel(BaseModel):
    email: Email


def test_email() -> None:
    model = DummyModel.model_validate({"email": "wasd@def.ghi"})
    assert model.email == "wasd@def.ghi"

    with pytest.raises(ValidationError):
        DummyModel.model_validate({"email": "foobar"})
