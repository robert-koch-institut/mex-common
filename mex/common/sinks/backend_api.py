from typing import Generator, Iterable

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import watch
from mex.common.models.base import MExModel
from mex.common.types import Identifier
from mex.common.utils import grouper


@watch
def post_to_backend_api(
    models: Iterable[MExModel], chunk_size: int = 100
) -> Generator[Identifier, None, None]:
    """Load models to the Backend API using bulk insertion.

    Args:
        models: Iterable of MEx models
        chunk_size: Optional size to chunks to post in one request

    Returns:
        Generator for identifiers of posted models
    """
    connector = BackendApiConnector.get()
    for chunk in grouper(chunk_size, models):
        model_list = list(filter(None, chunk))
        yield from connector.post_models(model_list)
