from mex.common.models.base import BaseModel


class AdditiveRule(BaseModel):
    """Base rule to add values to merged items."""


class SubtractiveRule(BaseModel):
    """Base rule to subtract values from merged items."""


class PreventiveRule(BaseModel):
    """Base rule to prevent primary sources for fields of merged items."""
