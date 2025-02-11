from typing import Annotated

from pydantic import Field, TypeAdapter

from mex.common.models import AnyMergedModel, AnyRuleSetResponse

MergedModelTypeAdapter: TypeAdapter[AnyMergedModel] = TypeAdapter(
    Annotated[AnyMergedModel, Field(discriminator="entityType")]
)
RuleSetResponseTypeAdapter: TypeAdapter[AnyRuleSetResponse] = TypeAdapter(
    Annotated[AnyRuleSetResponse, Field(discriminator="entityType")]
)
