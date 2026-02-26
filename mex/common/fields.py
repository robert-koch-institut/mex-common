from itertools import chain
from typing import cast

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
    AnyTemporalEntity,
    AnyVocabularyEnum,
    Link,
    LiteralStringType,
    TemporalEntityPrecision,
    Text,
)
from mex.common.utils import (
    contains_any_types,
    contains_only_types,
    get_all_fields,
    get_inner_types,
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

# all field types grouped by field and class names
ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES = {
    class_name: {
        field_name: list(get_inner_types(field_info.annotation, include_none=False))
        for field_name, field_info in get_all_fields(model_class).items()
    }
    for class_name, model_class in ALL_MODEL_CLASSES_BY_NAME.items()
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

# allowed temporal precisions grouped by field and class names
TEMPORAL_PRECISIONS_BY_FIELD_BY_CLASS_NAMES = {
    class_name: {
        field_name: sorted(
            {
                precision
                for temporal_type in ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES[class_name][
                    field_name
                ]
                for precision in cast(
                    "type[AnyTemporalEntity]", temporal_type
                ).ALLOWED_PRECISION_LEVELS
            },
            key=lambda precision: list(TemporalEntityPrecision).index(precision),
        )
        for field_name in field_names
    }
    for class_name, field_names in TEMPORAL_FIELDS_BY_CLASS_NAME.items()
}

# fields annotated as any vocabulary enum
VOCABULARY_FIELDS_BY_CLASS_NAME = group_fields_by_class_name(
    ALL_MODEL_CLASSES_BY_NAME,
    lambda field_info: contains_only_types(field_info, *VOCABULARY_ENUMS),
)

# vocabulary enum items grouped by field and class names
VOCABULARIES_BY_FIELDS_BY_CLASS_NAMES = {
    class_name: {
        field_name: [
            item
            for vocabulary in ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES[class_name][field_name]
            for item in cast("type[AnyVocabularyEnum]", vocabulary)
        ]
        for field_name in field_names
    }
    for class_name, field_names in VOCABULARY_FIELDS_BY_CLASS_NAME.items()
}

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

# list of fields by class name that are not allowed to be null or an empty list
REQUIRED_FIELDS_BY_CLASS_NAME = {
    name: sorted(
        {
            field_name
            for field_name, field_info in cls.model_fields.items()
            if field_info.is_required()
        }
    )
    for name, cls in ALL_MODEL_CLASSES_BY_NAME.items()
}

# fields that should be indexed as searchable fields
SEARCHABLE_FIELDS = sorted(
    {
        field_name
        for field_names in STRING_FIELDS_BY_CLASS_NAME.values()
        for field_name in field_names
    }
)

# classes that have fields that should be searchable
SEARCHABLE_CLASSES = sorted(
    {
        class_name
        for class_name, field_names in STRING_FIELDS_BY_CLASS_NAME.items()
        if field_names
    }
)

# allowed nested types grouped by fields
NESTED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME = {
    class_name: {
        field_name: sorted(
            nested_name
            for nested_name, nested_class in NESTED_MODEL_CLASSES_BY_NAME.items()
            if nested_class in field_types
        )
        for field_name, field_types in types_by_fields.items()
    }
    for class_name, types_by_fields in ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES.items()
}

# all nested types grouped by class name
NESTED_ENTITY_TYPES_BY_CLASS_NAME = {
    class_name: sorted(set(chain(*types_by_field.values())))
    for class_name, types_by_field in (
        NESTED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME.items()
    )
}

# allowed entity types grouped for reference fields
REFERENCED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME = {
    class_name: {
        field_name: sorted(
            identifier_class.__name__.removesuffix("Identifier")
            for identifier_class in MERGED_IDENTIFIER_CLASSES
            if contains_any_types(
                get_all_fields(ALL_MODEL_CLASSES_BY_NAME[class_name])[field_name],
                identifier_class,
            )
        )
        for field_name in field_names
    }
    for class_name, field_names in REFERENCE_FIELDS_BY_CLASS_NAME.items()
}

# stringified allowed types grouped by field and class names
STRINGIFIED_TYPES_BY_FIELD_BY_CLASS_NAME = {
    class_name: {
        field_name: REFERENCED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME[class_name].get(
            field_name, sorted(str(field_type.__name__) for field_type in field_types)
        )
        for field_name, field_types in fields.items()
    }
    for class_name, fields in ALL_TYPES_BY_FIELDS_BY_CLASS_NAMES.items()
}

# all referenced entity types grouped by class name
REFERENCED_ENTITY_TYPES_BY_CLASS_NAME = {
    class_name: sorted(set(chain(*types_by_field.values())))
    for class_name, types_by_field in (
        REFERENCED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME.items()
    )
}

# tuples of referenced type, referencing field, referencing type
REFERENCED_FIELD_REFERENCING_TUPLES = [
    (identifier_class.removesuffix("Identifier"), field_name, class_name)
    for class_name, types_by_field in (
        REFERENCED_ENTITY_TYPES_BY_FIELD_BY_CLASS_NAME.items()
    )
    for field_name, identifier_classes in types_by_field.items()
    for identifier_class in identifier_classes
]

# inbound reference fields by class name
INBOUND_REFERENCE_FIELDS_BY_CLASS_NAME = {
    target_class: {
        field_name: [
            source_class
            for t_class, f_name, source_class in REFERENCED_FIELD_REFERENCING_TUPLES
            if t_class == target_class and f_name == field_name
        ]
        for field_name in {
            f_name
            for t_class, f_name, _ in REFERENCED_FIELD_REFERENCING_TUPLES
            if t_class == target_class
        }
    }
    for target_class in {
        t_class for t_class, _, _ in REFERENCED_FIELD_REFERENCING_TUPLES
    }
}

# fields from any extracted class that contain references
ALL_REFERENCE_FIELD_NAMES = sorted(
    {
        field_name
        for class_name in EXTRACTED_MODEL_CLASSES_BY_NAME
        for field_name in REFERENCE_FIELDS_BY_CLASS_NAME[class_name]
    }
)
