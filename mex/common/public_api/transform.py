from collections import defaultdict

from mex.common.models import MODEL_CLASSES_BY_ENTITY_TYPE
from mex.common.models.base import MExModel
from mex.common.public_api.models import (
    PublicApiField,
    PublicApiFieldValueTypes,
    PublicApiItem,
)
from mex.common.types import Link, LinkLanguage, Text, TextLanguage


def transform_mex_model_to_public_api_item(
    model: MExModel,
) -> PublicApiItem:
    """Convert a MExModel instance into a Public API item.

    Args:
        model: Instance of a subclass of MExModel

    Returns:
        Public API item
    """
    api_values = []
    model_dict = model.dict(exclude_none=True)
    for field_name in sorted(model_dict):
        field = model.__fields__[field_name]
        if field.type_ in (Text, Link):
            model_values = getattr(model, field_name)
        else:
            model_values = model_dict[field_name]
        if not isinstance(model_values, list):
            model_values = [model_values]
        for value in model_values:
            if field.type_ in (Text, Link):
                language = value.language
                value = str(value)
            else:
                language = None
            api_values.append(
                PublicApiField(
                    fieldName=field_name, fieldValue=value, language=language
                )
            )

    return PublicApiItem(entityType=model.get_entity_type(), values=api_values)


def transform_public_api_item_to_mex_model(
    api_item: PublicApiItem,
) -> MExModel | None:
    """Try to convert a Public API item into an extracted data instance.

    Args:
        api_item: Public API item

    Returns:
        Instance of a subclass of MExModel or None if unknown type
    """
    if api_item.entityType not in MODEL_CLASSES_BY_ENTITY_TYPE:
        return None
    cls = MODEL_CLASSES_BY_ENTITY_TYPE[api_item.entityType]
    dct_to_parse: dict[str, list[PublicApiFieldValueTypes]] = defaultdict(list)
    for value in api_item.values:
        field_name = value.fieldName
        if isinstance(value.fieldValue, list):
            values = value.fieldValue
        else:
            values = [value.fieldValue]
        for v in values:
            if (
                value.language
                and isinstance(v, str)
                and cls.__fields__[field_name].type_ == Text
            ):
                dct_to_parse[field_name].append(
                    Text(value=v, language=TextLanguage(value.language))
                )
            elif (
                value.language
                and isinstance(v, str)
                and cls.__fields__[field_name].type_ == Link
            ):
                link = Link.from_orm(v)
                link.language = LinkLanguage(value.language)
                dct_to_parse[field_name].append(link)
            else:
                dct_to_parse[field_name].append(v)
    return cls.parse_obj(dct_to_parse)
