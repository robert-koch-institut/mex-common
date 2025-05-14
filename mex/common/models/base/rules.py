from typing import TYPE_CHECKING

from mex.common.models.base.model import BaseModel


class AdditiveRule(BaseModel, extra="forbid"):
    """Base rule to add values to merged items."""


class SubtractiveRule(BaseModel, extra="forbid"):
    """Base rule to subtract values from merged items."""


class PreventiveRule(BaseModel, extra="forbid"):
    """Base rule to prevent primary sources for fields of merged items."""


class RuleSet(BaseModel, extra="forbid"):
    """Base class for a set of an additive, subtractive and preventive rule."""

    if TYPE_CHECKING:  # pragma: no cover
        additive: AdditiveRule
        subtractive: SubtractiveRule
        preventive: PreventiveRule
