from collections.abc import Generator, Iterable

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.models import AnyExtractedModel, AnyMergedModel, AnyRuleSetResponse
from mex.common.sinks.base import BaseSink
from mex.common.utils import grouper


class BackendApiSink(BaseSink):
    """Sink to load models to the Backend API."""

    CHUNK_SIZE = 50

    def load(
        self, items: Iterable[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse]
    ) -> Generator[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse, None, None]:
        """Load extracted models or rule-sets to the Backend API using bulk insertion.

        Args:
            items: Iterable of extracted models or merged models or rule-sets

        Raises:
            NotImplementedError: When you try to load merged items into the backend

        Returns:
            Generator for posted models
        """
        total_count = 0
        connector = BackendApiConnector.get()
        for chunk in grouper(self.CHUNK_SIZE, items):
            model_list = []
            for model in chunk:
                if isinstance(model, AnyExtractedModel | AnyRuleSetResponse):
                    model_list.append(model)
                elif model is not None:
                    msg = f"backend cannot ingest {type(model)}"
                    raise NotImplementedError(msg)
            connector.ingest(model_list)
            total_count += len(model_list)
            yield from model_list
            logger.info("%s - written %s models", type(self).__name__, total_count)
