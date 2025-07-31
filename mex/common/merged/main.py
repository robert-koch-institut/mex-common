from collections.abc import Iterable, Mapping
from itertools import chain
from typing import Literal, cast, overload

from pydantic_core import ValidationError

from mex.common.exceptions import MergingError
from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.logging import logger
from mex.common.models import (
    MERGED_MODEL_CLASSES_BY_NAME,
    MEX_PRIMARY_SOURCE_STABLE_TARGET_ID,
    PREVIEW_MODEL_CLASSES_BY_NAME,
    RULE_SET_REQUEST_CLASSES_BY_NAME,
    AnyExtractedModel,
    AnyMergedModel,
    AnyPreviewModel,
    AnyRuleSetRequest,
    AnyRuleSetResponse,
)
from mex.common.transform import ensure_prefix
from mex.common.types import (
    AnyPrimitiveType,
    Identifier,
    MergedPrimarySourceIdentifier,
    Validation,
)
from mex.common.utils import ensure_list

SourcesAndValues = Iterable[tuple[MergedPrimarySourceIdentifier, AnyPrimitiveType]]
ValueList = list[AnyPrimitiveType]
SourceList = list[MergedPrimarySourceIdentifier]


def _pick_usable_values(
    field: str,
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse,
    validation: Literal[Validation.STRICT, Validation.LENIENT, Validation.IGNORE],
) -> ValueList:
    extracted_sources_and_values: SourcesAndValues = [
        (extracted_item.hadPrimarySource, value)
        for extracted_item in extracted_items
        for value in cast("ValueList", ensure_list(getattr(extracted_items, field)))
    ]
    additive_rule_sources_and_values: SourcesAndValues = [
        (MEX_PRIMARY_SOURCE_STABLE_TARGET_ID, value)
        for value in cast("ValueList", ensure_list(getattr(rule_set.additive, field)))
    ]
    subtracted_values: ValueList = cast(
        "ValueList", ensure_list(getattr(rule_set.subtractive, field))
    )
    prevented_sources: SourceList = cast(
        "SourceList", ensure_list(getattr(rule_set.preventive, field))
    )
    possible_sources_and_values: SourcesAndValues = chain(
        extracted_sources_and_values, additive_rule_sources_and_values
    )
    usable_values: ValueList = [
        value
        for source, value in possible_sources_and_values
        if source not in prevented_sources and value not in subtracted_values
    ]
    allow_lenient_fallback = validation is Validation.LENIENT
    if not usable_values and allow_lenient_fallback:
        subtractive_rule_sources_and_values: SourcesAndValues = (
            (MEX_PRIMARY_SOURCE_STABLE_TARGET_ID, value) for value in subtracted_values
        )
        for _, value in chain(
            extracted_sources_and_values,
            additive_rule_sources_and_values,
            subtractive_rule_sources_and_values,
        ):
            return [value]
    return usable_values


def _create_merged_dict(
    mergeable_fields: Iterable[str],
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse,
    validation: Literal[Validation.STRICT, Validation.LENIENT, Validation.IGNORE],
) -> dict[str, list[AnyPrimitiveType]]:
    return {
        field: _pick_usable_values(
            field,
            extracted_items,
            rule_set,
            validation,
        )
        for field in mergeable_fields
    }


@overload
def create_merged_item(
    identifier: Identifier,
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validation: Literal[Validation.LENIENT],
) -> AnyPreviewModel: ...


@overload
def create_merged_item(
    identifier: Identifier,
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validation: Literal[Validation.STRICT],
) -> AnyMergedModel: ...


@overload
def create_merged_item(
    identifier: Identifier,
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validation: Literal[Validation.IGNORE],
) -> AnyMergedModel: ...


def create_merged_item(
    identifier: Identifier,
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validation: Literal[Validation.STRICT, Validation.LENIENT, Validation.IGNORE],
) -> AnyPreviewModel | AnyMergedModel | None:
    """Merge a list of extracted items with a set of rules.

    Args:
        identifier: Identifier the finished merged item should have
        extracted_items: List of extracted items, can be empty
        rule_set: Rule set, with potentially empty rules
        validation: Controls how strictly the merged item needs to validate:
            - STRICT: Validates all required fields and list lengths. Returns a
                fully validated merged item or raises MergingError on validation failure
            - LENIENT: Skips validation checks and returns a "preview" merged item
                that may be missing required fields and even may be using blocked values
            - IGNORE: In case of validation errors, this mode will safely return None

    Raises:
        MergingError: When the given items cannot be merged (in STRICT mode)
        MergingError: When neither extracted nor rule items are given (in STRICT mode)

    Returns:
        Instance of a merged or preview item
    """
    model_class_lookup: Mapping[str, type[AnyPreviewModel | AnyMergedModel]]
    if validation == Validation.LENIENT:
        model_prefix = "Preview"
        model_class_lookup = PREVIEW_MODEL_CLASSES_BY_NAME
    else:
        model_prefix = "Merged"
        model_class_lookup = MERGED_MODEL_CLASSES_BY_NAME

    if rule_set:
        stem_type = rule_set.stemType
    elif extracted_items:
        extracted_items = sorted(extracted_items, key=lambda e: e.identifier)
        stem_type = extracted_items[0].stemType
    elif validation == Validation.STRICT:
        msg = "One of rule_set or extracted_items is required."
        raise MergingError(msg)
    else:
        logger.debug("One of rule_set or extracted_items is required.")
        return None

    entity_type = ensure_prefix(stem_type, model_prefix)
    fields = MERGEABLE_FIELDS_BY_CLASS_NAME[entity_type]
    cls = model_class_lookup[entity_type]
    if rule_set is None:
        rule_set = RULE_SET_REQUEST_CLASSES_BY_NAME[stem_type]()
    merged_dict = _create_merged_dict(fields, extracted_items, rule_set, validation)
    merged_dict["identifier"] = [str(identifier)]

    try:
        return cls.model_validate(merged_dict)
    except ValidationError as error:
        msg = "Could not validate merged model."
        if validation == Validation.STRICT:
            raise MergingError(msg) from error
        logger.debug("%s %s:%s", msg, entity_type, identifier)
    return None
