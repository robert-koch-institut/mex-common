from collections.abc import Generator, Iterable
from typing import cast

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.models import AnyExtractedModel
from mex.common.sinks.base import BaseSink
from mex.common.types import AnyExtractedIdentifier
from mex.common.utils import grouper


class BackendApiSink(BaseSink, BackendApiConnector):
    """Sink to load models to the Backend API."""

    CHUNK_SIZE = 50
    TIMEOUT = 30

    def load(
        self,
        models: Iterable[AnyExtractedModel],
    ) -> Generator[AnyExtractedIdentifier, None, None]:
        """Load models to the Backend API using bulk insertion.

        Args:
            models: Iterable of extracted models

        Returns:
            Generator for identifiers of posted models
        """
        total_count = 0
        for chunk in grouper(self.CHUNK_SIZE, models):
            model_list = [model for model in chunk if model is not None]
            response = self.post_extracted_items(model_list)
            total_count += len(model_list)
            yield from cast(list[AnyExtractedIdentifier], response.identifiers)
            logger.info("%s - written %s models", type(self).__name__, total_count)
