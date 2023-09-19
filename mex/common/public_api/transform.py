from collections import defaultdict
from typing import get_args

from mex.common.models import (
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MERGED_MODEL_CLASSES_BY_NAME,
    MExModel,
)
from mex.common.public_api.models import (
    PublicApiField,
    PublicApiFieldValueTypes,
    PublicApiItem,
)
from mex.common.types import Link, LinkLanguage, Text, TextLanguage


def transform_mex_model_to_public_api_item(model: MExModel) -> PublicApiItem:
    """Convert an ExtractedData instance into a Public API item.

    Args:
        model: Instance of a subclass of ExtractedData

    Returns:
        Public API item
    """
    api_values = []
    model_dict = model.model_dump(exclude_none=True)
    for field_name in sorted(model_dict):
        field = model.model_fields[field_name]
        is_text_or_link = any(
            type_ in (Text, Link)
            for type_ in [field.annotation, *get_args(field.annotation)]
        )
        if is_text_or_link:
            model_values = getattr(model, field_name)
        else:
            model_values = model_dict[field_name]
        if not isinstance(model_values, list):
            model_values = [model_values]
        for value in model_values:
            if is_text_or_link:
                language = value.language
                value = str(value)
            else:
                language = None
            api_values.append(
                PublicApiField(
                    fieldName=field_name, fieldValue=value, language=language
                )
            )
    return PublicApiItem(
        entityType=model.get_entity_type(),
        businessId=model.stableTargetId,
        values=api_values,
    )


def transform_public_api_item_to_mex_model(
    api_item: PublicApiItem,
) -> MExModel | None:
    """Try to convert a Public API item into an extracted data instance.

    Args:
        api_item: Public API item

    Returns:
        Transformed model or None if unknown type
    """
    classes_by_name: dict[str, type[MExModel]] = dict(
        **EXTRACTED_MODEL_CLASSES_BY_NAME, **MERGED_MODEL_CLASSES_BY_NAME
    )
    cls = classes_by_name.get(api_item.entityType)
    if cls is None:
        return None
    dct_to_parse: dict[str, list[PublicApiFieldValueTypes]] = defaultdict(list)
    for value in api_item.values:
        field_name = value.fieldName
        annotation = cls.model_fields[field_name].annotation
        is_link = any(type_ is Link for type_ in [annotation, *get_args(annotation)])
        is_text = any(type_ is Text for type_ in [annotation, *get_args(annotation)])
        if isinstance(value.fieldValue, list):
            values = value.fieldValue
        else:
            values = [value.fieldValue]
        for v in values:
            if value.language and isinstance(v, str) and is_text:
                dct_to_parse[field_name].append(
                    Text(value=v, language=TextLanguage(value.language))
                )
            elif value.language and isinstance(v, str) and is_link:
                link = Link.model_validate(v)
                link.language = LinkLanguage(value.language)
                dct_to_parse[field_name].append(link)
            else:
                dct_to_parse[field_name].append(v)
    return cls.model_validate(dct_to_parse)
