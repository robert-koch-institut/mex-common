from abc import abstractmethod
from collections.abc import Generator, Iterable

from mex.common.connector import BaseConnector
from mex.common.models import AnyExtractedModel, AnyMergedModel, AnyRuleSetResponse


class BaseSink(BaseConnector):
    """Base class to define the interface of sink instances."""

    def __init__(self) -> None:
        """Create a new sink."""

    def close(self) -> None:
        """Close the sink."""

    @abstractmethod
    def load(
        self,
        items: Iterable[AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse],
    ) -> Generator[
        AnyExtractedModel | AnyMergedModel | AnyRuleSetResponse, None, None
    ]:  # pragma: no cover
        """Load the given items to a destination and yield them."""
        ...
