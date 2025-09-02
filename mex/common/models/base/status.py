from pydantic import BaseModel


class Status(BaseModel):
    """Model for system status responses."""

    status: str


class VersionStatus(Status):
    """Model for system status responses with a version."""

    version: str
