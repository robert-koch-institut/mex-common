import json
from collections.abc import Generator, Iterable
from contextlib import ExitStack
from pathlib import Path
from typing import IO, Any

from mex.common.logging import logger, watch
from mex.common.models import AnyExtractedModel
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder
from mex.common.types import AnyExtractedIdentifier


@watch
def write_ndjson(
    models: Iterable[AnyExtractedModel],
) -> Generator[AnyExtractedIdentifier, None, None]:
    """Write the incoming models into a new-line delimited JSON file.

    Args:
        models: Iterable of extracted models to write

    Settings:
        work_dir: Path to store the NDJSON files in

    Returns:
        Generator for identifiers of written models
    """
    file_handles: dict[str, IO[Any]] = {}
    settings = BaseSettings.get()
    with ExitStack() as stack:
        for model in models:
            class_name = model.__class__.__name__
            try:
                handle = file_handles[class_name]
            except KeyError:
                file_name = Path(settings.work_dir, f"{class_name}.ndjson")
                writer = open(file_name, "a+", encoding="utf-8")  # noqa: SIM115
                file_handles[class_name] = handle = stack.enter_context(writer)
                logger.info(
                    "write_ndjson - writing %s to file %s",
                    class_name,
                    file_name.as_posix(),
                )

            json.dump(model, handle, sort_keys=True, cls=MExEncoder)
            handle.write("\n")
            yield model.identifier
