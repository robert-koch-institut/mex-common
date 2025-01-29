import json
from collections.abc import Generator, Iterable
from contextlib import ExitStack
from pathlib import Path
from typing import IO, Any

from mex.common.logging import logger
from mex.common.models import (
    AnyExtractedModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
)
from mex.common.settings import BaseSettings
from mex.common.sinks.base import BaseSink
from mex.common.transform import MExEncoder
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
        models_or_rule_sets: Iterable[
            AnyExtractedModel | AnyRuleSetRequest | AnyRuleSetResponse
        ],
    ) -> Generator[
        AnyExtractedModel | AnyRuleSetRequest | AnyRuleSetResponse, None, None
    ]:
        """Write models or rule-sets into a new-line delimited JSON file.

        Args:
            models_or_rule_sets: Extracted models, rule-set requests or responses

        Returns:
            Generator for the loaded models or rules.
        """
        file_handles: dict[str, IO[Any]] = {}
        total_count = 0
        with ExitStack() as stack:
            for chunk in grouper(self.CHUNK_SIZE, models_or_rule_sets):
                for model_or_rule_set in chunk:
                    if model_or_rule_set is None:
                        continue
                    class_name = model_or_rule_set.__class__.__name__
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
                    dumped_json = json.dumps(
                        model_or_rule_set, sort_keys=True, cls=MExEncoder
                    )
                    fh.write(f"{dumped_json}\n")
                    total_count += 1
                    yield model_or_rule_set
                logger.info("%s - written %s items", type(self).__name__, total_count)
