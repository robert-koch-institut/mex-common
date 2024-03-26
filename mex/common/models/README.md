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
PreventiveX:    all fields as of merged primary source identifiers
