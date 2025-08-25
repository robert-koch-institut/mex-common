from collections.abc import Iterable, Mapping
from itertools import chain
from typing import Literal, cast, overload

from pydantic_core import ValidationError

from mex.common.exceptions import MergingError
from mex.common.fields import MERGEABLE_FIELDS_BY_CLASS_NAME
from mex.common.logging import logger
from mex.common.merged.types import (
    SourceAndValueIter,
    SourceAndValueList,
    SourceList,
    ValueList,
)
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
from mex.common.types import AnyPrimitiveType, AnyValidation, Identifier, Validation
from mex.common.utils import ensure_list


def _collect_extracted_values(
    field: str,
    extracted_items: Iterable[AnyExtractedModel],
) -> SourceAndValueList:
    """Collect values from extracted items for a specific field.

    Args:
        field: Name of the field to extract values from
        extracted_items: Iterable of extracted model instances

    Returns:
        List of (source, value) tuples from the extracted items
    """
    return [
        (extracted_item.hadPrimarySource, value)
        for extracted_item in extracted_items
        for value in cast("ValueList", ensure_list(getattr(extracted_item, field)))
    ]


def _collect_additive_values(
    field: str,
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse,
) -> SourceAndValueList:
    """Collect values from additive rules for a specific field.

    Args:
        field: Name of the field to extract values from
        rule_set: Rule set containing additive rules

    Returns:
        List of (source, value) tuples from the additive rules
    """
    return [
        (MEX_PRIMARY_SOURCE_STABLE_TARGET_ID, value)
        for value in cast("ValueList", ensure_list(getattr(rule_set.additive, field)))
    ]


def _collect_subtractive_values(
    field: str,
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse,
) -> ValueList:
    """Collect values from subtractive rules for a specific field.

    Args:
        field: Name of the field to extract values from
        rule_set: Rule set containing subtractive rules

    Returns:
        List of values that should be subtracted/removed
    """
    return cast("ValueList", ensure_list(getattr(rule_set.subtractive, field)))


def _collect_preventive_sources(
    field: str,
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse,
) -> SourceList:
    """Collect sources from preventive rules for a specific field.

    Args:
        field: Name of the field to extract sources from
        rule_set: Rule set containing preventive rules

    Returns:
        List of sources that should be prevented/blocked
    """
    return cast("SourceList", ensure_list(getattr(rule_set.preventive, field)))


def _filter_usable_values(
    possible_sources_and_values: SourceAndValueIter,
    prevented_sources: SourceList,
    subtracted_values: ValueList,
) -> ValueList:
    """Filter values by removing prevented sources and subtracted values.

    Args:
        possible_sources_and_values: Iterable of (source, value) tuples to filter
        prevented_sources: List of sources that should be excluded
        subtracted_values: List of values that should be excluded

    Returns:
        List of unique, filtered values
    """
    seen_values = set()
    usable_values = []

    for source, value in possible_sources_and_values:
        if (
            source not in prevented_sources
            and value not in subtracted_values
            and value not in seen_values
        ):
            seen_values.add(value)
            usable_values.append(value)

    return usable_values


def _apply_lenient_fallback(
    extracted_sources_and_values: SourceAndValueIter,
    additive_rule_sources_and_values: SourceAndValueIter,
    subtracted_values: ValueList,
) -> ValueList:
    """Apply lenient fallback by returning first available value from any source.

    Args:
        extracted_sources_and_values: (source, value) tuples from extracted items
        additive_rule_sources_and_values: (source, value) tuples from additive rules
        subtracted_values: Values that were subtracted/removed

    Returns:
        List containing the first available value, or empty list if none found
    """
    subtractive_rule_sources_and_values: SourceAndValueIter = (
        (MEX_PRIMARY_SOURCE_STABLE_TARGET_ID, value) for value in subtracted_values
    )
    for _, value in chain(
        extracted_sources_and_values,
        additive_rule_sources_and_values,
        subtractive_rule_sources_and_values,
    ):
        return [value]
    return []


def _pick_usable_values(
    field: str,
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse,
    validation: AnyValidation,
) -> ValueList:
    """Pick usable values for a field from given extracted items and rules.

    Args:
        field: Name of the field to process
        extracted_items: Iterable of extracted model instances
        rule_set: Rule set containing additive, subtractive, and preventive rules
        validation: Validation mode (STRICT, LENIENT, or IGNORE)

    Returns:
        List of usable values after applying all rules and validation logic
    """
    # Collect values from extracted items and rules
    extracted_sources_and_values = _collect_extracted_values(field, extracted_items)
    additive_rule_sources_and_values = _collect_additive_values(field, rule_set)
    subtracted_values = _collect_subtractive_values(field, rule_set)
    prevented_sources = _collect_preventive_sources(field, rule_set)

    # Combine possible sources and filter them
    possible_sources_and_values = chain(
        extracted_sources_and_values, additive_rule_sources_and_values
    )
    usable_values = _filter_usable_values(
        possible_sources_and_values, prevented_sources, subtracted_values
    )

    # Apply lenient fallback if needed
    allow_lenient_fallback = validation is Validation.LENIENT
    if not usable_values and allow_lenient_fallback:
        return _apply_lenient_fallback(
            extracted_sources_and_values,
            additive_rule_sources_and_values,
            subtracted_values,
        )

    return usable_values


def _create_merged_dict(
    mergeable_fields: Iterable[str],
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse,
    validation: AnyValidation,
) -> dict[str, list[AnyPrimitiveType] | AnyPrimitiveType]:
    """Create a merged dictionary by processing all mergeable fields.

    Args:
        mergeable_fields: Names of fields that should be processed for merging
        extracted_items: Iterable of extracted model instances
        rule_set: Rule set containing additive, subtractive, and preventive rules
        validation: Validation mode (STRICT, LENIENT, or IGNORE)

    Returns:
        Dictionary mapping field names to lists of merged values
    """
    return {
        field: _pick_usable_values(
            field,
            extracted_items,
            rule_set,
            validation,
        )
        for field in mergeable_fields
    }


def _get_merged_class(
    extracted_items: list[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validation: AnyValidation,
) -> type[AnyMergedModel | AnyPreviewModel] | None:
    """Determine the appropriate merged model class based on validation mode.

    Args:
        extracted_items: List of extracted model instances
        rule_set: Rule set containing entity type information, or None
        validation: Validation mode determining whether to use Preview or Merged models

    Returns:
        The appropriate model class (Preview* for LENIENT, Merged* for STRICT/IGNORE),
        or None if neither extracted_items nor rule_set was given.
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
        stem_type = extracted_items[0].stemType
    else:
        return None

    entity_type = ensure_prefix(stem_type, model_prefix)
    return model_class_lookup[entity_type]


def _ensure_rule_set(
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    stem_type: str,
) -> AnyRuleSetRequest | AnyRuleSetResponse:
    """Ensure a rule set instance exists, creating a default one if needed.

    Args:
        rule_set: Existing rule set instance, or None to create a default
        stem_type: Entity stem type (e.g., "Person", "ContactPoint") for creation

    Returns:
        A rule set instance (either the provided one or a newly created default)

    Raises:
        KeyError: If stem_type does not correspond to a valid rule set class
    """
    if rule_set is None:
        rule_set_class_name = f"{stem_type}RuleSetRequest"
        rule_set = RULE_SET_REQUEST_CLASSES_BY_NAME[rule_set_class_name]()
    return rule_set


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
) -> AnyMergedModel | None: ...


def create_merged_item(
    identifier: Identifier,
    extracted_items: Iterable[AnyExtractedModel],
    rule_set: AnyRuleSetRequest | AnyRuleSetResponse | None,
    validation: AnyValidation,
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
    # Convert extracted items from any iterable into sorted list
    extracted_items = sorted(extracted_items, key=lambda e: e.identifier)

    # Get merged class based on extracted and rule items and validation mode
    merged_class = _get_merged_class(extracted_items, rule_set, validation)

    # Bail out when neither extracted nor rule items are given
    if merged_class is None:
        if validation == Validation.STRICT:
            msg = "One of rule_set or extracted_items is required."
            raise MergingError(msg)
        logger.debug("One of rule_set or extracted_items is required.")
        return None

    # Get mergeable fields and ensure rule set instance
    fields = MERGEABLE_FIELDS_BY_CLASS_NAME[merged_class.__name__]
    rule_set = _ensure_rule_set(rule_set, merged_class.stemType)

    # Create a dictionary of merged values and set the merged identifier
    merged_dict = _create_merged_dict(fields, extracted_items, rule_set, validation)
    merged_dict["identifier"] = identifier

    # Try to parse the dictionary of merged values into a pydantic model
    try:
        return merged_class.model_validate(merged_dict)
    except ValidationError as error:
        msg = "Could not validate merged model."
        if validation == Validation.STRICT:
            raise MergingError(msg) from error
        logger.debug("%s %s:%s", msg, merged_class.__name__, identifier)
    return None
