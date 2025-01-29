from abc import abstractmethod
from collections.abc import Generator, Iterable

from mex.common.connector import BaseConnector
from mex.common.models import AnyExtractedModel, AnyRuleSetRequest, AnyRuleSetResponse


class BaseSink(BaseConnector):
    """Base class to define the interface of sink instances."""

    def __init__(self) -> None:
        """Create a new sink."""

    def close(self) -> None:
        """Close the sink."""

    @abstractmethod
    def load(
        self,
        models_or_rule_sets: Iterable[
            AnyExtractedModel | AnyRuleSetRequest | AnyRuleSetResponse
        ],
    ) -> Generator[
        AnyExtractedModel | AnyRuleSetRequest | AnyRuleSetResponse, None, None
    ]:  # pragma: no cover
        """Load extracted models or rule-sets to a destination and yield them."""
        ...
