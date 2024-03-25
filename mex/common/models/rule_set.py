from typing import Any, Literal, cast, get_args

from pydantic import Field, create_model

from mex.common.models.base import BaseModel
from mex.common.types import MergedPrimarySourceIdentifier


class AdditiveRule(BaseModel):
    """Base rule to add values to merged items."""


class SubtractiveRule(BaseModel):
    """Base rule to subtract values from merged items."""


class BlockingRule(BaseModel):
    """Base rule to block primary sources for fields of merged items."""


LiteralType = type(Literal["Type"])


def create_blocking_rule(
    blocking_literal: Any, sparse_model: type[BaseModel], doc: str
) -> type[BaseModel]:
    """Dynamically create and return a new model class for a blocking rule."""
    if not isinstance(blocking_literal, LiteralType):
        raise TypeError("need a literal string to create a blocking rule")
    blocking_name = str(get_args(blocking_literal)[0])
    return create_model(
        blocking_name,
        __base__=(
            sparse_model,
            BlockingRule,
        ),
        __doc__=doc,
        __module__=sparse_model.__module__,
        entityType=(
            blocking_literal,
            Field(default=blocking_name, alias="$type", frozen=True),
        ),
        **{
            field: cast(
                Any,
                (
                    list[MergedPrimarySourceIdentifier],
                    cast(list[MergedPrimarySourceIdentifier], []),
                ),
            )
            for field in sparse_model.model_fields
        }
    )
