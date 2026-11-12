import pytest

from mex.common.models import (
    ADDITIVE_MODEL_CLASSES,
    BASE_MODEL_CLASSES_BY_NAME,
    EXTRACTED_MODEL_CLASSES,
    MERGED_MODEL_CLASSES,
    PREVIEW_MODEL_CLASSES,
    SUBTRACTIVE_MODEL_CLASSES,
    AnyAdditiveModel,
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnySubtractiveModel,
)

VARIANT_MODEL_CLASSES = [
    *EXTRACTED_MODEL_CLASSES,
    *MERGED_MODEL_CLASSES,
    *PREVIEW_MODEL_CLASSES,
    *ADDITIVE_MODEL_CLASSES,
    *SUBTRACTIVE_MODEL_CLASSES,
]


@pytest.mark.parametrize(
    "model", VARIANT_MODEL_CLASSES, ids=lambda model: model.__name__
)
def test_variant_fields_are_documented_like_base_fields(
    model: type[
        AnyExtractedModel
        | AnyMergedModel
        | AnyPreviewModel
        | AnyAdditiveModel
        | AnySubtractiveModel
    ],
) -> None:
    base_model = BASE_MODEL_CLASSES_BY_NAME[f"Base{model.stemType}"]
    shared_field_names = set(base_model.model_fields) & set(model.model_fields)

    assert {
        name: (info.description, info.json_schema_extra)
        for name, info in model.model_fields.items()
        if name in shared_field_names
    } == {
        name: (info.description, info.json_schema_extra)
        for name, info in base_model.model_fields.items()
        if name in shared_field_names
    }
