from collections.abc import Sequence
from typing import Any, Literal, overload

from pydantic_core import ValidationError

from mex.common.exceptions import MergingError
from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.merged.utils import extend_list_in_dict, prune_list_in_dict
from mex.common.models import (
    MERGED_MODEL_CLASSES_BY_NAME,
    PREVIEW_MODEL_CLASSES_BY_NAME,
    AnyAdditiveModel,
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreventiveModel,
    AnyPreviewModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
    AnySubtractiveModel,
)
from mex.common.transform import ensure_prefix
from mex.common.types import Identifier


def _merge_extracted_items_and_apply_preventive_rule(
    merged_dict: dict[str, Any],
    mergeable_fields: Sequence[str],
    extracted_items: Sequence[AnyExtractedModel],
    rule: AnyPreventiveModel | None,
) -> None:
    """Merge a list of extracted items while applying a preventive rule.

    Collect unique values from the extracted items and write them into `merged_dict`,
    unless the primary source of the extracted item was blocked by the rule.

    Args:
        merged_dict: Mapping from field names to lists of merged values
        mergeable_fields: List of mergeable field names
        extracted_items: List of extracted items
        rule: Preventive rules with primary source identifiers, can be None
    """
    for extracted_item in sorted(extracted_items, key=lambda e: e.identifier):
        for field_name in mergeable_fields:
            if rule is not None and extracted_item.hadPrimarySource in getattr(
                rule, field_name
            ):
                continue
            extracted_value = getattr(extracted_item, field_name)
            extend_list_in_dict(merged_dict, field_name, extracted_value)


def _apply_additive_rule(
    merged_dict: dict[str, Any],
    mergeable_fields: Sequence[str],
    rule: AnyAdditiveModel,
) -> None:
    """Merge the values from an additive rule into a `merged_dict`.

    Args:
        merged_dict: Mapping from field names to lists of merged values
        mergeable_fields: List of mergeable field names
        rule: Additive rule with values to be added
    """
    for field_name in mergeable_fields:
        rule_value = getattr(rule, field_name)
        extend_list_in_dict(merged_dict, field_name, rule_value)


def _apply_subtractive_rule(
    merged_dict: dict[str, Any],
    mergeable_fields: Sequence[str],
    rule: AnySubtractiveModel,
) -> None:
    """Prune values of a subtractive rule from a `merged_dict`.

    Args:
        merged_dict: Mapping from field names to lists of merged values
        mergeable_fields: List of mergeable field names
        rule: Subtractive rule with values to remove
    """
    for field_name in mergeable_fields:
        rule_value = getattr(rule, field_name)
        prune_list_in_dict(merged_dict, field_name, rule_value)


@overload
def create_merged_item(
    identifier: Identifier,
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validate_cardinality: Literal[False],
) -> AnyPreviewModel: ...


@overload
def create_merged_item(
    identifier: Identifier,
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validate_cardinality: Literal[True],
) -> AnyMergedModel: ...


def create_merged_item(
    identifier: Identifier,
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validate_cardinality: Literal[True, False],
) -> AnyPreviewModel | AnyMergedModel:
    """Merge a list of extracted items with a set of rules.

    Args:
        identifier: Identifier the finished merged item should have
        extracted_items: List of extracted items, can be empty
        rule_set: Rule set, with potentially empty rules
        validate_cardinality: Merged items validate the existence of required fields and
            the lengths of lists, set this to `False` to avoid this and return a
            "preview" of a merged item instead of a valid merged item

    Raises:
        MergingError: When the given items cannot be merged

    Returns:
        Instance of a merged or preview item
    """
    model_class_lookup: (
        dict[str, type[AnyPreviewModel]] | dict[str, type[AnyMergedModel]]
    )
    if validate_cardinality:
        model_prefix = "Merged"
        model_class_lookup = MERGED_MODEL_CLASSES_BY_NAME
    else:
        model_prefix = "Preview"
        model_class_lookup = PREVIEW_MODEL_CLASSES_BY_NAME

    if rule_set:
        entity_type = ensure_prefix(rule_set.stemType, model_prefix)
    elif extracted_items:
        entity_type = ensure_prefix(extracted_items[0].stemType, model_prefix)
    else:
        msg = "One of rule_set or extracted_items is required."
        raise MergingError(msg)
    fields = MERGEABLE_FIELDS_BY_CLASS_NAME[entity_type]
    cls = model_class_lookup[entity_type]

    merged_dict: dict[str, Any] = {"identifier": identifier}

    _merge_extracted_items_and_apply_preventive_rule(
        merged_dict, fields, extracted_items, rule_set.preventive if rule_set else None
    )
    if rule_set:
        _apply_additive_rule(merged_dict, fields, rule_set.additive)
        _apply_subtractive_rule(merged_dict, fields, rule_set.subtractive)
    try:
        return cls.model_validate(merged_dict)
    except ValidationError as error:
        msg = "Could not validate merged model."
        raise MergingError(msg) from error
