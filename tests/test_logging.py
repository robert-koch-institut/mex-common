import logging
from collections.abc import Generator
from uuid import UUID

from pytest import LogCaptureFixture

from mex.common.exceptions import MExError
from mex.common.logging import watch


def test_watch(caplog: LogCaptureFixture) -> None:
    items: list[str | UUID | MExError] = [
        "foo",
        UUID(int=16, version=4),
        MExError("foo", 42),
    ]

    @watch(log_interval=1)
    def dummy_generator() -> Generator[str | UUID | MExError, None, None]:
        yield from items

    # unpack generator and capture logs
    with caplog.at_level(logging.INFO, logger="mex"):
        yielded_items = list(dummy_generator())

    # check that returned items are untouched
    assert yielded_items == items

    # check captured logging
    assert len(caplog.messages) == 3
    str_line, uuid_line, error_line = caplog.messages
    assert "dummy_generator - foo" in str_line
    assert "dummy_generator - 00000000-0000-4000-8000-000000000010" in uuid_line
    assert "dummy_generator - MExError: foo, 42" in error_line
