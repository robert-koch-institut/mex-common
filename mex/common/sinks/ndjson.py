import json
from collections.abc import Generator, Iterable
from contextlib import ExitStack
from pathlib import Path
from typing import IO, Any

from mex.common.logging import logger
from mex.common.models import AnyExtractedModel
from mex.common.settings import BaseSettings
from mex.common.sinks.base import BaseSink
from mex.common.transform import MExEncoder
from mex.common.types import AnyExtractedIdentifier
from mex.common.utils import grouper


class NdjsonSink(BaseSink):
    """Sink to load models into new-line delimited JSON files."""

    CHUNK_SIZE = 100
    _work_dir: Path

    def __init__(self) -> None:
        """Instantiate the multi sink singleton."""
        settings = BaseSettings.get()
        self._work_dir = Path(settings.work_dir)

    def close(self) -> None:
        """Nothing to close, since load already closes all file handles."""

    def load(
        self,
        models: Iterable[AnyExtractedModel],
    ) -> Generator[AnyExtractedIdentifier, None, None]:
        """Write models into a new-line delimited JSON file.

        Args:
            models: Iterable of extracted models to write

        Returns:
            Generator for identifiers of written models
        """
        file_handles: dict[str, IO[Any]] = {}
        total_count = 0
        with ExitStack() as stack:
            for chunk in grouper(self.CHUNK_SIZE, models):
                for model in chunk:
                    if model is None:
                        continue
                    class_name = model.__class__.__name__
                    try:
                        fh = file_handles[class_name]
                    except KeyError:
                        file_name = self._work_dir / f"{class_name}.ndjson"
                        writer = open(file_name, "a+", encoding="utf-8")  # noqa: SIM115
                        file_handles[class_name] = fh = stack.enter_context(writer)
                        logger.info(
                            "NdjsonSink - writing %s to file %s",
                            class_name,
                            file_name.as_posix(),
                        )
                    fh.write(f"{json.dumps(model, sort_keys=True, cls=MExEncoder)}\n")
                    total_count += 1
                    yield model.identifier
                logger.info("NdjsonSink - written %s models", total_count)
