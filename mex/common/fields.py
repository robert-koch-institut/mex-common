from mex.common.models import (
    ADDITIVE_MODEL_CLASSES_BY_NAME,
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MERGED_MODEL_CLASSES_BY_NAME,
    PREVENTIVE_MODEL_CLASSES_BY_NAME,
    PREVIEW_MODEL_CLASSES_BY_NAME,
    SUBTRACTIVE_MODEL_CLASSES_BY_NAME,
)
from mex.common.types import (
    MERGED_IDENTIFIER_CLASSES,
    NESTED_MODEL_CLASSES_BY_NAME,
    TEMPORAL_ENTITIES,
    VOCABULARY_ENUMS,
    Email,
    Link,
    LiteralStringType,
    Text,
)
from mex.common.utils import (
    contains_only_types,
    get_all_fields,
    group_fields_by_class_name,
)

# all models classes
ALL_MODEL_CLASSES_BY_NAME = {
    **ADDITIVE_MODEL_CLASSES_BY_NAME,
    **EXTRACTED_MODEL_CLASSES_BY_NAME,
    **MERGED_MODEL_CLASSES_BY_NAME,
    **NESTED_MODEL_CLASSES_BY_NAME,
    **PREVIEW_MODEL_CLASSES_BY_NAME,
    **PREVENTIVE_MODEL_CLASSES_BY_NAME,
    **SUBTRACTIVE_MODEL_CLASSES_BY_NAME,
}

# fields that are immutable and can only be set once
FROZEN_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: field_info.frozen is True,
)

# static fields that are set once on class-level to a literal type
LITERAL_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: isinstance(field_info.annotation, LiteralStringType),
)

# fields typed as merged identifiers containing references to merged items
REFERENCE_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, *MERGED_IDENTIFIER_CLASSES),
)

# nested fields that contain `Text` objects
TEXT_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, Text),
)

# nested fields that contain `Link` objects
LINK_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, Link),
)

# fields annotated as `Email` type
EMAIL_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, Email),
)

# fields annotated as `int` type
INTEGER_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, int),
)

# fields annotated as `str` type
STRING_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, str),
)

# fields annotated as any temporal type
TEMPORAL_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, *TEMPORAL_ENTITIES),
)

# fields annotated as any vocabulary enum
VOCABULARY_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, *VOCABULARY_ENUMS),
)

# fields with changeable values that are not nested objects or merged item references
MUTABLE_FIELDS_BY_CLASS_NAME = {
    name: sorted(
        {
            field_name
            for field_name in get_all_fields(cls)
            if field_name
            not in (
                *FROZEN_FIELDS_BY_CLASS_NAME[name],
                *REFERENCE_FIELDS_BY_CLASS_NAME[name],
                *TEXT_FIELDS_BY_CLASS_NAME[name],
                *LINK_FIELDS_BY_CLASS_NAME[name],
            )
        }
    )
    for name, cls in ALL_MODEL_CLASSES_BY_NAME.items()
}

# fields with mergeable values that are neither literal nor frozen
MERGEABLE_FIELDS_BY_CLASS_NAME = {
    name: sorted(
        {
            field_name
            for field_name in get_all_fields(cls)
            if field_name
            not in (
                *FROZEN_FIELDS_BY_CLASS_NAME[name],
                *LITERAL_FIELDS_BY_CLASS_NAME[name],
            )
        }
    )
    for name, cls in ALL_MODEL_CLASSES_BY_NAME.items()
}

# fields with values that should be set once but are neither literal nor references
FINAL_FIELDS_BY_CLASS_NAME = {
    name: sorted(
        {
            field_name
            for field_name in get_all_fields(cls)
            if field_name in FROZEN_FIELDS_BY_CLASS_NAME[name]
            and field_name
            not in (
                *LITERAL_FIELDS_BY_CLASS_NAME[name],
                *REFERENCE_FIELDS_BY_CLASS_NAME[name],
            )
        }
    )
    for name, cls in ALL_MODEL_CLASSES_BY_NAME.items()
}
