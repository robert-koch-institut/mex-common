from mex.common.models.base.model import BaseModel
from mex.common.transform import camel_to_split


class MergedItem(
    BaseModel,
    extra="forbid",
    model_title_generator=lambda m: camel_to_split(m.__name__),
):
    """Base model for all merged item classes."""
