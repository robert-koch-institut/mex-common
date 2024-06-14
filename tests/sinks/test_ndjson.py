from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import UUID4

from mex.common.models import ExtractedData
from mex.common.settings import BaseSettings
from mex.common.sinks.ndjson import write_ndjson
from mex.common.types import (
    ExtractedIdentifier,
    Identifier,
    MergedIdentifier,
    TemporalEntity,
)


class DummyEnum(Enum):
    NAME = "value"


class Thing(ExtractedData[ExtractedIdentifier, MergedIdentifier]):
    entityType: Literal["Thing"] = "Thing"
    str_attr: str
    enum_attr: DummyEnum | None = None
    uuid_attr: UUID4 | None = None
    ts_attr: TemporalEntity | None = None


def test_write_ndjson() -> None:
    settings = BaseSettings.get()

    test_models = [
        Thing(
            hadPrimarySource=Identifier.generate(41),
            identifierInPrimarySource="1",
            str_attr="foo",
        ),
        Thing(
            hadPrimarySource=Identifier.generate(42),
            identifierInPrimarySource="2",
            str_attr="bar",
            enum_attr=DummyEnum.NAME,
        ),
        Thing(
            hadPrimarySource=Identifier.generate(43),
            identifierInPrimarySource="3",
            str_attr="baz",
            uuid_attr=UUID(int=42, version=4),
        ),
        Thing(
            hadPrimarySource=Identifier.generate(44),
            identifierInPrimarySource="4",
            str_attr="dat",
            ts_attr=TemporalEntity(2000, 1, 1),
        ),
    ]

    ids = list(write_ndjson(test_models))
    assert ids == [m.identifier for m in test_models]

    with open(settings.work_dir / "Thing.ndjson") as handle:
        output = handle.read()

    assert (
        output
        == """{"entityType": "Thing", "enum_attr": null, "hadPrimarySource": "bFQoRhcVH5DHU5", "identifier": "eBBkb544HJi9Fuvr6Ogf27", "identifierInPrimarySource": "1", "stableTargetId": "g1zzwSdgfOfcimsSRtIKja", "str_attr": "foo", "ts_attr": null, "uuid_attr": null}
{"entityType": "Thing", "enum_attr": "value", "hadPrimarySource": "bFQoRhcVH5DHU6", "identifier": "ulVMQQ87fDrv3O6WAhgo3", "identifierInPrimarySource": "2", "stableTargetId": "fSOS56LUmJz4MSDUKwUAVr", "str_attr": "bar", "ts_attr": null, "uuid_attr": null}
{"entityType": "Thing", "enum_attr": null, "hadPrimarySource": "bFQoRhcVH5DHU7", "identifier": "faPTaLe0LHG2w0izPjuTP3", "identifierInPrimarySource": "3", "stableTargetId": "fbEI02h2ASTxd441B9fyxr", "str_attr": "baz", "ts_attr": null, "uuid_attr": "00000000-0000-4000-8000-00000000002a"}
{"entityType": "Thing", "enum_attr": null, "hadPrimarySource": "bFQoRhcVH5DHU8", "identifier": "cEDoKScSEuGPbo4jFD5cfd", "identifierInPrimarySource": "4", "stableTargetId": "eeyCEYnqXC8xKgPPrlK1HJ", "str_attr": "dat", "ts_attr": "2000-01-01", "uuid_attr": null}
"""
    )
