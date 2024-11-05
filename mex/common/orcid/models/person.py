from mex.common.models import BaseModel


class ORCIDperson(BaseModel):
    """Model class for an orcid person."""

    name: str

    @staticmethod
    def get_orcid_fields() -> tuple[str, ...]:  # noqa: D102
        return tuple(sorted(ORCIDperson.model_fields))
