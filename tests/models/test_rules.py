from mex.common.models import BASE_MODEL_CLASSES_BY_NAME, PREVENTIVE_MODEL_CLASSES
from mex.common.transform import ensure_prefix
from mex.common.types import MergedPrimarySourceIdentifier


def test_preventive_models_define_same_fields_as_base_model() -> None:
    for preventive_rule in PREVENTIVE_MODEL_CLASSES:
        base_model_name = ensure_prefix(preventive_rule.stemType, "Base")
        base_model = BASE_MODEL_CLASSES_BY_NAME[base_model_name]
        expected_fields = {"entityType", *base_model.model_fields}
        assert set(preventive_rule.model_fields) == expected_fields


def test_preventive_models_define_all_fields_as_correct_type() -> None:
    for preventive_rule in PREVENTIVE_MODEL_CLASSES:
        for field_name, field_info in preventive_rule.model_fields.items():
            if field_name == "entityType":
                assert field_info.default == preventive_rule.__name__
            else:
                assert field_info.annotation == list[MergedPrimarySourceIdentifier]
