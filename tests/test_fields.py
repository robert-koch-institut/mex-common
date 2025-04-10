from mex.common.fields import (
    ALL_MODEL_CLASSES_BY_NAME,
    EMAIL_FIELDS_BY_CLASS_NAME,
    FINAL_FIELDS_BY_CLASS_NAME,
    FROZEN_FIELDS_BY_CLASS_NAME,
    INTEGER_FIELDS_BY_CLASS_NAME,
    LINK_FIELDS_BY_CLASS_NAME,
    LITERAL_FIELDS_BY_CLASS_NAME,
    MERGEABLE_FIELDS_BY_CLASS_NAME,
    MUTABLE_FIELDS_BY_CLASS_NAME,
    REFERENCE_FIELDS_BY_CLASS_NAME,
    STRING_FIELDS_BY_CLASS_NAME,
    TEMPORAL_FIELDS_BY_CLASS_NAME,
    TEXT_FIELDS_BY_CLASS_NAME,
    VOCABULARY_FIELDS_BY_CLASS_NAME,
)


def test_all_fields_by_class_names_include_all_classes() -> None:
    assert {
        len(lookup)
        for lookup in (
            EMAIL_FIELDS_BY_CLASS_NAME,
            FINAL_FIELDS_BY_CLASS_NAME,
            FROZEN_FIELDS_BY_CLASS_NAME,
            INTEGER_FIELDS_BY_CLASS_NAME,
            LINK_FIELDS_BY_CLASS_NAME,
            LITERAL_FIELDS_BY_CLASS_NAME,
            MERGEABLE_FIELDS_BY_CLASS_NAME,
            MUTABLE_FIELDS_BY_CLASS_NAME,
            REFERENCE_FIELDS_BY_CLASS_NAME,
            STRING_FIELDS_BY_CLASS_NAME,
            TEMPORAL_FIELDS_BY_CLASS_NAME,
            TEXT_FIELDS_BY_CLASS_NAME,
            VOCABULARY_FIELDS_BY_CLASS_NAME,
        )
    } == {len(ALL_MODEL_CLASSES_BY_NAME)}
