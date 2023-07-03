from typing import Callable, Iterable

from mex.common.exceptions import MExError
from mex.common.models.base import MExModel
from mex.common.settings import BaseSettings
from mex.common.sinks import Sink
from mex.common.sinks.backend_api import post_to_backend_api
from mex.common.sinks.ndjson import write_ndjson
from mex.common.sinks.public_api import post_to_public_api
from mex.common.types import Identifier


def load(models: Iterable[MExModel]) -> None:
    """Load models to the MEx public or backend APIs or write to NDJSON files.

    Args:
        models: Iterable of MEx models

    Settings:
        sink: Where to load the provided models
    """
    settings = BaseSettings.get()
    sink: Callable[[Iterable[MExModel]], Iterable[Identifier]]
    if settings.sink == Sink.BACKEND:
        sink = post_to_backend_api
    elif settings.sink == Sink.PUBLIC:
        sink = post_to_public_api
    elif settings.sink == Sink.NDJSON:
        sink = write_ndjson
    else:
        raise MExError(f"Cannot load to {settings.sink}")

    for _ in sink(models):
        continue  # unpacking the generator
