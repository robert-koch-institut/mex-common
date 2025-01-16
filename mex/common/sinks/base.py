from abc import abstractmethod
from collections.abc import Iterable

from mex.common.connector import BaseConnector
from mex.common.models import AnyExtractedModel
from mex.common.types import Identifier


class BaseSink(BaseConnector):
    """Base class to define the interface of sink instances."""

    @abstractmethod
    def load(
        self, models: Iterable[AnyExtractedModel]
    ) -> Iterable[Identifier]:  # pragma: no cover
        """Iteratively load models to a destination and yield their identifiers."""
        ...
