import json
from collections.abc import Generator, Iterable
from contextlib import ExitStack
from pathlib import Path
from typing import IO, Any, overload

from mex.common.logging import logger
from mex.common.models import AnyExtractedModel, AnyRuleModel
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

    @overload
    def load(
        self,
        models_or_rules: Iterable[AnyExtractedModel],
    ) -> Generator[AnyExtractedIdentifier, None, None]: ...

    @overload
    def load(
        self,
        models_or_rules: Iterable[AnyRuleModel],
    ) -> None: ...

    def load(
        self,
        models_or_rules: Iterable[AnyExtractedModel] | Iterable[AnyRuleModel],
    ) -> Generator[AnyExtractedIdentifier, None, None] | None:
        """Write models or rules into a new-line delimited JSON file.

        Args:
          models_or_rules: Iterable of extracted models or rules to write

        Returns:
          Generator for identifiers of written models or None if rules.
        """
        file_handles: dict[str, IO[Any]] = {}
        total_count = 0
        with ExitStack() as stack:
            for chunk in grouper(self.CHUNK_SIZE, models_or_rules):
                for model_or_rule in chunk:
                    if model_or_rule is None:
                        continue
                    class_name = model_or_rule.__class__.__name__
                    try:
                        fh = file_handles[class_name]
                    except KeyError:
                        file_name = self._work_dir / f"{class_name}.ndjson"
                        writer = open(file_name, "a+", encoding="utf-8")  # noqa: SIM115
                        file_handles[class_name] = fh = stack.enter_context(writer)
                        logger.info(
                            "%s - writing %s to file %s",
                            type(self).__name__,
                            class_name,
                            file_name.as_posix(),
                        )
                    fh.write(
                        f"{json.dumps(model_or_rule, sort_keys=True, cls=MExEncoder)}\n"
                    )
                    total_count += 1
                    if hasattr(model_or_rule, "identifier"):
                        yield model_or_rule.identifier
                logger.info("%s - written %s items", type(self).__name__, total_count)
        return None
