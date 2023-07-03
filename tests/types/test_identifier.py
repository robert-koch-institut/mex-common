from uuid import UUID

import pytest
from pydantic import BaseModel, ValidationError
from pytest import MonkeyPatch

from mex.common.types import Identifier


class DummyID(Identifier):
    REFERENCE = "#/components/Dummy#/id"


class DummyModel(BaseModel):
    id: Identifier
    dummy: DummyID | None = None


def test_identifier_validates() -> None:
    model_with_obj = DummyModel.parse_obj({"id": Identifier("bFQoRhcVH5DIfZ")})
    model_with_raw = DummyModel.parse_obj({"id": "bFQoRhcVH5DIfZ"})
    model_with_raw_uuid = DummyModel.parse_obj(
        {"id": "00000000-0000-4000-8000-000000000539"}
    )
    model_with_uuid_obj = DummyModel.parse_obj({"id": UUID(int=1337, version=4)})

    assert (
        model_with_obj.id
        == model_with_raw.id
        == model_with_raw_uuid.id
        == model_with_uuid_obj.id
        == Identifier.generate(seed=1337)
    )

    with pytest.raises(ValidationError):
        DummyModel.parse_obj({"id": "baaiaaaboi!!!"})

    with pytest.raises(ValidationError):
        DummyModel.parse_obj({"id": 42})


def test_identifier_modifies_schema() -> None:
    assert DummyModel.schema()["properties"]["id"] == {
        "title": "Identifier",
        "type": "string",
        "pattern": r"^[a-zA-Z0-9]{14,22}$",
    }
    assert DummyModel.schema()["properties"]["dummy"] == {
        "$ref": "#/components/Dummy#/id"
    }


def test_identifier_repr() -> None:
    assert repr(Identifier("baaiaaaaaaaboi")) == "Identifier('baaiaaaaaaaboi')"


def test_identifier_generate(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "mex.common.types.identifier.uuid4", lambda: UUID(int=42, version=4)
    )

    id_from_seed = Identifier.generate(seed=42)
    random_id = Identifier.generate()
    assert id_from_seed == random_id == Identifier("bFQoRhcVH5DHU6")
