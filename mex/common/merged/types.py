from collections.abc import Iterable

from mex.common.types import AnyPrimitiveType, MergedPrimarySourceIdentifier

SourceAndValueList = list[tuple[MergedPrimarySourceIdentifier, AnyPrimitiveType]]
SourceAndValueIter = Iterable[tuple[MergedPrimarySourceIdentifier, AnyPrimitiveType]]
ValueList = list[AnyPrimitiveType]
SourceList = list[MergedPrimarySourceIdentifier]
