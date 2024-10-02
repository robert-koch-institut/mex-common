from uuid import UUID

import pytest
from pydantic import BaseModel, ValidationError
from pytest import MonkeyPatch

from mex.common.types import IDENTIFIER_PATTERN, Identifier


class DummyIdentifier(Identifier):
    pass


class DummyModel(BaseModel):
    id: DummyIdentifier


def test_identifier_validation() -> None:
    model = DummyModel.model_validate({"id": "bFQoRhcVH5DIfZ"})
    assert model.id == DummyIdentifier("bFQoRhcVH5DIfZ")

    model = DummyModel.model_validate({"id": DummyIdentifier("bFQoRhcVH5DIfZ")})
    assert model.id == DummyIdentifier("bFQoRhcVH5DIfZ")

    model = DummyModel(id=DummyIdentifier("bFQoRhcVH5DIfZ"))
    assert model.id == DummyIdentifier("bFQoRhcVH5DIfZ")

    with pytest.raises(ValidationError):
        DummyModel.model_validate({"id": "baaiaaaboi!!!"})

    with pytest.raises(ValidationError):
        DummyModel.model_validate({"id": object()})


def test_identifier_serialization() -> None:
    model = DummyModel(id=DummyIdentifier("bFQoRhcVH5DIfZ"))
    raw = model.model_dump()

    assert raw == {"id": "bFQoRhcVH5DIfZ"}


def test_identifier_schema() -> None:
    assert DummyModel.model_json_schema() == {
        "properties": {
            "id": {
                "pattern": IDENTIFIER_PATTERN,
                "title": "DummyIdentifier",
                "type": "string",
            }
        },
        "required": ["id"],
        "title": "DummyModel",
        "type": "object",
    }


def test_identifier_repr() -> None:
    assert repr(Identifier("baaiaaaaaaaboi")) == 'Identifier("baaiaaaaaaaboi")'


def test_identifier_generate(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "mex.common.types.identifier.uuid4", lambda: UUID(int=42, version=4)
    )

    id_from_seed = Identifier.generate(seed=42)
    random_id = Identifier.generate()
    assert id_from_seed == random_id == Identifier("bFQoRhcVH5DHU6")
