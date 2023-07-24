from itertools import tee
from typing import Callable, Iterable

from mex.common.exceptions import MExError
from mex.common.models import MExModel
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
    sink_function: Callable[[Iterable[MExModel]], Iterable[Identifier]]

    for sink, model_gen in zip(settings.sink, tee(models, len(settings.sink))):
        if sink == Sink.BACKEND:
            sink_function = post_to_backend_api
        elif sink == Sink.PUBLIC:
            sink_function = post_to_public_api
        elif sink == Sink.NDJSON:
            sink_function = write_ndjson
        else:
            raise MExError(f"Cannot load to {sink}.")

        for _ in sink_function(model_gen):
            continue  # unpacking the generator
