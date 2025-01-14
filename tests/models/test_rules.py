from mex.common.models import (
    ADDITIVE_MODEL_CLASSES,
    BASE_MODEL_CLASSES_BY_NAME,
    EXTRACTED_MODEL_CLASSES,
    PREVENTIVE_MODEL_CLASSES,
    RULE_SET_REQUEST_CLASSES,
    RULE_SET_RESPONSE_CLASSES,
    SUBTRACTIVE_MODEL_CLASSES,
)
from mex.common.types import Identifier, MergedPrimarySourceIdentifier


def test_all_rules_are_defined() -> None:
    stem_types = sorted(c.stemType for c in EXTRACTED_MODEL_CLASSES)
    for lookup in (
        ADDITIVE_MODEL_CLASSES,
        PREVENTIVE_MODEL_CLASSES,
        RULE_SET_REQUEST_CLASSES,
        RULE_SET_RESPONSE_CLASSES,
        SUBTRACTIVE_MODEL_CLASSES,
    ):
        assert sorted(c.stemType for c in lookup) == stem_types


def test_additive_models_define_same_fields_as_base_model() -> None:
    for additive_rule in ADDITIVE_MODEL_CLASSES:
        base_model_name = "Base" + additive_rule.stemType
        base_model = BASE_MODEL_CLASSES_BY_NAME[base_model_name]
        expected_fields = {"entityType", *base_model.model_fields}
        assert set(additive_rule.model_fields) == expected_fields


def test_additive_models_have_no_required_fields() -> None:
    for additive_model in ADDITIVE_MODEL_CLASSES:
        model = additive_model()
        assert model.model_dump(exclude_unset=True) == {}


def test_subtractive_models_define_same_fields_as_base_model() -> None:
    for subtractive_rule in SUBTRACTIVE_MODEL_CLASSES:
        base_model_name = "Base" + subtractive_rule.stemType
        base_model = BASE_MODEL_CLASSES_BY_NAME[base_model_name]
        expected_fields = {"entityType", *base_model.model_fields}
        assert set(subtractive_rule.model_fields) == expected_fields


def test_subtractive_models_have_no_required_fields() -> None:
    for subtractive_model in SUBTRACTIVE_MODEL_CLASSES:
        model = subtractive_model()
        assert model.model_dump(exclude_unset=True) == {}


def test_preventive_models_define_same_fields_as_base_model() -> None:
    for preventive_rule in PREVENTIVE_MODEL_CLASSES:
        base_model_name = "Base" + preventive_rule.stemType
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
                assert field_info.is_required() is False
                assert field_info.default == []


def test_rule_set_request_models_have_no_required_fields() -> None:
    for rule_set_request in RULE_SET_REQUEST_CLASSES:
        model = rule_set_request()
        assert model.model_dump(exclude_unset=True) == {}


def test_rule_set_response_models_only_require_stable_target_id() -> None:
    for rule_set_response in RULE_SET_RESPONSE_CLASSES:
        model = rule_set_response(stableTargetId=Identifier.generate(seed=1))
        assert model.model_dump(exclude_unset=True) == {
            "stableTargetId": "bFQoRhcVH5DHUr"
        }
