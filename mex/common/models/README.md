
_OptionalLists:     0-n lists according to schema
_RequiredLists:     1-n lists according to schema
_SparseLists:       optionalized _RequiredLists for rules

_OptionalValues:    optional values according to schema
_RequiredValues:    required values according to schema
_SparseValues:      optionalized _RequiredValues for rules
_VariadicValues:    listified _OptionalValues and _RequiredValues for rules

BaseX:          _OptionalLists, _RequiredLists, _OptionalValues, _RequiredValues
ExtractedX:     BaseX, ExtractedData
MergedX:        BaseX, MergedItem
AdditiveX:      _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
SubtractiveX:   _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
PreventiveX:    all fields as list[MergedPrimarySourceIdentifier]



class AdditiveAccessPlatform(
    _OptionalLists, _SparseLists, _OptionalValues, _SparseValues, AdditiveRule
):
    """Rule to add values to merged access platform items."""

    entityType: Annotated[
        Literal["AdditiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "AdditiveAccessPlatform"


class SubtractiveAccessPlatform(
    _OptionalLists, _SparseLists, _VariadicValues, SubtractiveRule
):
    """Rule to subtract values from merged access platform items."""

    entityType: Annotated[
        Literal["SubtractiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "SubtractiveAccessPlatform"


class PreventiveAccessPlatform(PreventiveRule):
    """Rule to prevent primary sources for fields of merged access platform items."""

    entityType: Annotated[
        Literal["PreventiveAccessPlatform"], Field(alias="$type", frozen=True)
    ] = "PreventiveAccessPlatform"

    foo: list[MergedPrimarySourceIdentifier] = []
