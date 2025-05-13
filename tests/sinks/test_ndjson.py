from enum import Enum
from uuid import UUID

from pydantic import UUID4

from mex.common.models import BaseModel
from mex.common.settings import BaseSettings
from mex.common.sinks.ndjson import NdjsonSink
from mex.common.types import Identifier, TemporalEntity


class DummyEnum(Enum):
    NAME = "value"


class Thing(BaseModel):
    identifier: Identifier
    str_attr: str
    enum_attr: DummyEnum | None = None
    uuid_attr: UUID4 | None = None
    ts_attr: TemporalEntity | None = None


def test_sink_load() -> None:
    settings = BaseSettings.get()

    test_models = [
        Thing(identifier=Identifier.generate(seed=1), str_attr="foo"),
        Thing(
            identifier=Identifier.generate(seed=2),
            str_attr="bar",
            enum_attr=DummyEnum.NAME,
        ),
        Thing(
            identifier=Identifier.generate(seed=3),
            str_attr="baz",
            uuid_attr=UUID(int=42, version=4),
        ),
        Thing(
            identifier=Identifier.generate(seed=4),
            str_attr="dat",
            ts_attr=TemporalEntity(2000, 1, 1),
        ),
    ]

    sink = NdjsonSink.get()
    items = list(sink.load(test_models))
    assert len(items) == len(test_models)

    with (settings.work_dir / "Thing.ndjson").open() as fh:
        output = fh.read()

    expected = """\
{{"enum_attr": null, "identifier": "{}", "str_attr": "foo", "ts_attr": null, "uuid_attr": null}}
{{"enum_attr": "value", "identifier": "{}", "str_attr": "bar", "ts_attr": null, "uuid_attr": null}}
{{"enum_attr": null, "identifier": "{}", "str_attr": "baz", "ts_attr": null, "uuid_attr": "00000000-0000-4000-8000-00000000002a"}}
{{"enum_attr": null, "identifier": "{}", "str_attr": "dat", "ts_attr": "2000-01-01", "uuid_attr": null}}
""".format(*[m.identifier for m in test_models])

    assert output == expected
