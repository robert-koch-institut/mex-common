from pydantic import BaseModel as PydanticBaseModel


class Status(PydanticBaseModel):
    """Model for system status responses."""

    status: str


class VersionStatus(Status):
    """Model for system status responses with a version."""

    version: str
