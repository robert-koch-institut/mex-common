import logging

from click.testing import CliRunner
from pytest import LogCaptureFixture

from mex.common.cli import entrypoint
from mex.common.settings import BaseSettings


def test_good_entrypoint_exits_zero() -> None:
    @entrypoint(BaseSettings)
    def good_entrypoint() -> None:
        return

    result = CliRunner().invoke(good_entrypoint, args=[])
    assert result.exit_code == 0, result.output


def test_faulty_entrypoint_exits_non_zero() -> None:
    @entrypoint(BaseSettings)
    def faulty_entrypoint() -> None:
        _ = 1 / 0

    result = CliRunner().invoke(faulty_entrypoint, args=[])
    assert result.exit_code == 1, result.output


def test_entrypoint_logs_docs_and_settings(caplog: LogCaptureFixture) -> None:
    @entrypoint()
    def chatty_entrypoint() -> None:
        """Hi, I am Pointy McEntryFace."""
        return

    with caplog.at_level(logging.INFO, logger="mex"):
        result = CliRunner().invoke(chatty_entrypoint, args=["--pdb"])
    assert result.exit_code == 0, result.output

    assert "Pointy McEntryFace" in caplog.text
