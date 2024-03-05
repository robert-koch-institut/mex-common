from mex.common.models import BaseModel
from mex.common.types import Identifier


class BulkInsertResponse(BaseModel):
    """Response body for the bulk ingestion endpoint."""

    identifiers: list[Identifier]
