from uuid import UUID

import pytest
from pydantic import BaseModel, ValidationError
from pytest import MonkeyPatch

from mex.common.types import Identifier


class DummyID(Identifier):
    pass


class DummyModel(BaseModel):
    id: Identifier
    dummy: DummyID | None = None


def test_identifier_validates() -> None:
    model_with_obj = DummyModel.model_validate({"id": Identifier("bFQoRhcVH5DIfZ")})
    model_with_raw = DummyModel.model_validate({"id": "bFQoRhcVH5DIfZ"})
    model_with_raw_uuid = DummyModel.model_validate(
        {"id": "00000000-0000-4000-8000-000000000539"}
    )
    model_with_uuid_obj = DummyModel.model_validate({"id": UUID(int=1337, version=4)})

    assert (
        model_with_obj.id
        == model_with_raw.id
        == model_with_raw_uuid.id
        == model_with_uuid_obj.id
        == Identifier.generate(seed=1337)
    )

    with pytest.raises(ValidationError):
        DummyModel.model_validate({"id": "baaiaaaboi!!!"})

    with pytest.raises(ValidationError):
        DummyModel.model_validate({"id": 42})


def test_identifier_modifies_schema() -> None:
    assert DummyModel.model_json_schema()["properties"]["id"] == {
        "title": "Identifier",
        "type": "string",
        "pattern": r"^[a-zA-Z0-9]{14,22}$",
    }
    assert DummyModel.model_json_schema()["properties"]["dummy"] == {
        "anyOf": [
            {"pattern": "^[a-zA-Z0-9]{14,22}$", "title": "DummyID", "type": "string"},
            {"type": "null"},
        ],
        "default": None,
        "title": "Dummy",
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
