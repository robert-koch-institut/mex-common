import json
from collections.abc import Generator, Iterable
from contextlib import ExitStack
from pathlib import Path
from typing import IO, Any, TypeVar

from mex.common.logging import logger, watch
from mex.common.models.base.model import BaseModel
from mex.common.settings import BaseSettings
from mex.common.sinks.base import BaseSink
from mex.common.transform import MExEncoder
from mex.common.utils import grouper

_LoadItemT = TypeVar("_LoadItemT", bound=BaseModel)


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

    @watch(log_interval=1000)
    def load(
        self,
        items: Iterable[_LoadItemT],
    ) -> Generator[_LoadItemT, None, None]:
        """Write any items into a new-line delimited JSON file.

        Args:
            items: Iterable of any kind of items

        Returns:
            Generator for the loaded items
        """
        file_handles: dict[str, IO[Any]] = {}
        with ExitStack() as stack:
            for chunk in grouper(self.CHUNK_SIZE, items):
                for item in chunk:
                    if item is None:
                        continue
                    class_name = item.__class__.__name__
                    try:
                        fh = file_handles[class_name]
                    except KeyError:
                        file = self._work_dir / f"{class_name}.ndjson"
                        writer = file.open("a+", encoding="utf-8")
                        file_handles[class_name] = fh = stack.enter_context(writer)
                        logger.info(
                            "%s - writing %s to file %s",
                            type(self).__name__,
                            class_name,
                            file.as_posix(),
                        )
                    dumped_json = json.dumps(
                        item, sort_keys=True, cls=MExEncoder, ensure_ascii=False
                    )
                    fh.write(f"{dumped_json}\n")
                    yield item
