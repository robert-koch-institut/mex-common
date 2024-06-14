from typing import TypeVar, cast

from mex.common.identity.models import Identity
from mex.common.identity.registry import get_provider
from mex.common.models import ExtractedData
from mex.common.types import ExtractedIdentifier, MergedIdentifier

ExtractedIdentifierT = TypeVar("ExtractedIdentifierT", bound=ExtractedIdentifier)
MergedIdentifierT = TypeVar("MergedIdentifierT", bound=MergedIdentifier)


def assign_identity(
    model: ExtractedData[ExtractedIdentifierT, MergedIdentifierT]
) -> Identity[ExtractedIdentifierT, MergedIdentifierT]:
    """Find an Identity for a given extracted item or assign a new one."""
    provider = get_provider()
    return cast(
        Identity[ExtractedIdentifierT, MergedIdentifierT],
        provider.assign(model.hadPrimarySource, model.identifierInPrimarySource),
    )
