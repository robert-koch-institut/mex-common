import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from pytest import LogCaptureFixture

from mex.common.exceptions import MExError
from mex.common.logging import echo, get_ts, watch


def test_watch(caplog: LogCaptureFixture) -> None:
    items = ["foo", UUID(int=16, version=4), MExError("foo", 42)]

    @watch
    def dummy_generator() -> Any:
        yield from items

    # unpack generator and capture logs
    with caplog.at_level(logging.INFO, logger="mex"):
        yielded_items = list(dummy_generator())

    # check that returned items are untouched
    assert yielded_items == items

    # check captured logging
    assert len(caplog.messages) == 3
    str_line, uuid_line, error_line = caplog.messages
    assert "[dummy generator] foo" in str_line
    assert "[dummy generator] 00000000-0000-4000-8000-000000000010" in uuid_line
    assert "[dummy generator] MExError: foo, 42" in error_line


def test_get_ts() -> None:
    assert get_ts(datetime(1999, 12, 31, 23, 59, 59)) == (
        "\x1b[93m[1999-12-31 23:59:59]\x1b[0m"
    )


def test_echo(caplog: LogCaptureFixture) -> None:
    # echo while capturing logs
    with caplog.at_level(logging.INFO, logger="mex"):
        echo("This is going well", ts=datetime(1999, 12, 31, 23, 59, 59))

    assert "[1999-12-31 23:59:59] This is going well" in caplog.text
