from mex.common.models.entity import BaseEntity


class AdditiveRule(BaseEntity):
    """Base rule to add values to merged items."""


class SubtractiveRule(BaseEntity):
    """Base rule to subtract values from merged items."""


class PreventiveRule(BaseEntity):
    """Base rule to prevent primary sources for fields of merged items."""
