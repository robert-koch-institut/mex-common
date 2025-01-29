from collections.abc import Generator, Iterable

from mex.common.backend_api.connector import BackendApiConnector
from mex.common.logging import logger
from mex.common.models import AnyExtractedModel, AnyRuleSetRequest, AnyRuleSetResponse
from mex.common.sinks.base import BaseSink
from mex.common.utils import grouper


class BackendApiSink(BaseSink):
    """Sink to load models to the Backend API."""

    CHUNK_SIZE = 50

    def load(
        self,
        models_or_rule_sets: Iterable[
            AnyExtractedModel | AnyRuleSetRequest | AnyRuleSetResponse
        ],
    ) -> Generator[
        AnyExtractedModel | AnyRuleSetRequest | AnyRuleSetResponse, None, None
    ]:
        """Load extracted models or rule-sets to the Backend API using bulk insertion.

        Args:
            models_or_rule_sets: Iterable of extracted models or rule-sets

        Returns:
            Generator for posted models
        """
        total_count = 0
        connector = BackendApiConnector.get()
        for chunk in grouper(self.CHUNK_SIZE, models_or_rule_sets):
            model_list = [model for model in chunk if model is not None]
            connector.ingest(model_list)
            total_count += len(model_list)
            yield from model_list
            logger.info("%s - written %s models", type(self).__name__, total_count)
