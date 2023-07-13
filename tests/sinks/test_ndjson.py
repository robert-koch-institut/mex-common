from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import UUID4

from mex.common.models import MExModel
from mex.common.settings import BaseSettings
from mex.common.sinks.ndjson import write_ndjson
from mex.common.types import Timestamp


class DummyEnum(Enum):
    NAME = "value"


class Thing(MExModel):
    str_attr: str
    enum_attr: Optional[DummyEnum]
    uuid_attr: Optional[UUID4]
    ts_attr: Optional[Timestamp]

    @classmethod
    def get_entity_type(cls) -> str:
        return "Thing"


def test_write_ndjson() -> None:
    settings = BaseSettings.get()

    test_models = [
        Thing.construct(identifier="1", str_attr="foo"),
        Thing.construct(identifier="2", str_attr="bar", enum_attr=DummyEnum.NAME),
        Thing.construct(
            identifier="3", str_attr="baz", uuid_attr=UUID(int=42, version=4)
        ),
        Thing.construct(identifier="4", str_attr="dat", ts_attr=Timestamp(2000, 1, 1)),
    ]

    ids = list(write_ndjson(test_models))
    assert len(ids)

    with open(settings.work_dir / "Thing.ndjson", "r") as handle:
        output = handle.read()

    expected = """\
{"enum_attr": null, "identifier": "%s", "str_attr": "foo", "ts_attr": null, "uuid_attr": null}
{"enum_attr": "value", "identifier": "%s", "str_attr": "bar", "ts_attr": null, "uuid_attr": null}
{"enum_attr": null, "identifier": "%s", "str_attr": "baz", "ts_attr": null, "uuid_attr": "00000000-0000-4000-8000-00000000002a"}
{"enum_attr": null, "identifier": "%s", "str_attr": "dat", "ts_attr": "2000-01-01", "uuid_attr": null}
""" % tuple(
        m.identifier for m in test_models
    )

    assert output == expected
