from enum import Enum
from uuid import UUID

from pydantic import UUID4

from mex.common.models import ExtractedData
from mex.common.settings import BaseSettings
from mex.common.sinks.ndjson import write_ndjson
from mex.common.types import Identifier, Timestamp


class DummyEnum(Enum):
    NAME = "value"


class Thing(ExtractedData):
    identifier: Identifier
    str_attr: str
    enum_attr: DummyEnum | None = None
    uuid_attr: UUID4 | None = None
    ts_attr: Timestamp | None = None


def test_write_ndjson() -> None:
    settings = BaseSettings.get()

    test_models = [
        Thing.model_construct(identifier="1", str_attr="foo"),
        Thing.model_construct(identifier="2", str_attr="bar", enum_attr=DummyEnum.NAME),
        Thing.model_construct(
            identifier="3", str_attr="baz", uuid_attr=UUID(int=42, version=4)
        ),
        Thing.model_construct(
            identifier="4", str_attr="dat", ts_attr=Timestamp(2000, 1, 1)
        ),
    ]

    ids = list(write_ndjson(test_models))
    assert len(ids)

    with open(settings.work_dir / "Thing.ndjson") as handle:
        output = handle.read()

    expected = """\
{{"enum_attr": null, "identifier": "{}", "str_attr": "foo", "ts_attr": null, "uuid_attr": null}}
{{"enum_attr": "value", "identifier": "{}", "str_attr": "bar", "ts_attr": null, "uuid_attr": null}}
{{"enum_attr": null, "identifier": "{}", "str_attr": "baz", "ts_attr": null, "uuid_attr": "00000000-0000-4000-8000-00000000002a"}}
{{"enum_attr": null, "identifier": "{}", "str_attr": "dat", "ts_attr": "2000-01-01", "uuid_attr": null}}
""".format(
        *[m.identifier for m in test_models]
    )

    assert output == expected
