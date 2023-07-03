from mex.common.models.base import BaseModel
from mex.common.types import Identifier


class BulkInsertResponse(BaseModel):
    """Response body for the bulk ingestion endpoint."""

    identifiers: list[Identifier]
