import json
from contextlib import ExitStack
from pathlib import Path
from typing import IO, Any, Generator, Iterable

from mex.common.logging import echo, watch
from mex.common.models import MExModel
from mex.common.settings import BaseSettings
from mex.common.transform import MExEncoder
from mex.common.types import Identifier


@watch
def write_ndjson(models: Iterable[MExModel]) -> Generator[Identifier, None, None]:
    """Write the incoming models into a new-line delimited JSON file.

    Args:
        models: Iterable of models to write

    Settings:
        work_dir: Path to store the NDJSON files in

    Returns:
        Generator for identifiers of written models
    """
    file_handles: dict[str, IO[Any]] = {}
    settings = BaseSettings.get()
    with ExitStack() as stack:
        for model in models:
            entity_type = model.get_entity_type()
            try:
                handle = file_handles[entity_type]
            except KeyError:
                file_name = Path(settings.work_dir, f"{entity_type}.ndjson")
                writer = open(file_name, "a+", encoding="utf-8")
                file_handles[entity_type] = handle = stack.enter_context(writer)
                echo(
                    f"[writing {entity_type} to file] {file_name.as_posix()}",
                    fg="green",
                )

            json.dump(model, handle, sort_keys=True, cls=MExEncoder)
            handle.write("\n")
            yield model.identifier
