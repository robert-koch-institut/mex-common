from typing import Annotated, Any

import pytest
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, ValidationError

from mex.common.fields import REQUIRED_FIELDS_BY_CLASS_NAME
from mex.common.models import (
    EXTRACTED_MODEL_CLASSES_BY_NAME,
    MERGED_MODEL_CLASSES,
    AnyMergedModel,
    MergedPerson,
)
from mex.common.models.base.merged_item import UNGATED_FIELD_NAMES, MergedItem


def get_error_types_by_field(error: ValidationError) -> dict[str, str]:
    return {str(e["loc"][0]): e["type"] for e in error.errors()}


@pytest.mark.parametrize("model", MERGED_MODEL_CLASSES, ids=lambda m: m.__name__)
def test_required_unless_superseded_matches_extracted_model(
    model: type[AnyMergedModel],
) -> None:
    extracted_model = EXTRACTED_MODEL_CLASSES_BY_NAME[
        model.__name__.replace("Merged", "Extracted", 1)
    ]
    expected = sorted(
        {
            name
            for name, field_info in extracted_model.model_fields.items()
            if field_info.is_required()
        }
        - {"hadPrimarySource", "identifierInPrimarySource"}
    )
    assert expected  # every entity has at least one required field
    assert list(model.requiredUnlessSuperseded) == expected


@pytest.mark.parametrize("model", MERGED_MODEL_CLASSES, ids=lambda m: m.__name__)
def test_required_fields_by_class_name_include_gated_fields(
    model: type[AnyMergedModel],
) -> None:
    assert REQUIRED_FIELDS_BY_CLASS_NAME[model.__name__] == sorted(
        ["identifier", *model.requiredUnlessSuperseded]
    )


@pytest.mark.parametrize("model", MERGED_MODEL_CLASSES, ids=lambda m: m.__name__)
def test_active_item_without_required_fields_is_invalid(
    model: type[AnyMergedModel],
) -> None:
    with pytest.raises(ValidationError) as error:
        model.model_validate({"identifier": "someIdentifier1234567"})

    assert get_error_types_by_field(error.value) == {
        name: "too_short" if model.model_fields[name].default == [] else "missing"
        for name in model.requiredUnlessSuperseded
    }


@pytest.mark.parametrize("model", MERGED_MODEL_CLASSES, ids=lambda m: m.__name__)
def test_superseded_item_without_other_fields_is_valid(
    model: type[AnyMergedModel],
) -> None:
    item = model.model_validate(
        {
            "identifier": "someIdentifier1234567",
            "supersededBy": "supersededBy8901234567",
        }
    )

    assert item.supersededBy == "supersededBy8901234567"
    for name in model.requiredUnlessSuperseded:
        assert getattr(item, name) == model.model_fields[name].default
    # serialized superseded items, including their defaults, validate again
    assert model.model_validate(item.model_dump()) == item


def test_superseded_item_with_leftover_values_is_invalid(
    merged_person: MergedPerson,
) -> None:
    data: dict[str, Any] = {
        **merged_person.model_dump(),
        "supersededBy": "supersededBy8901234567",
    }

    with pytest.raises(ValidationError) as error:
        MergedPerson.model_validate(data)

    assert get_error_types_by_field(error.value) == {
        name: "superseded_value"
        for name in MergedPerson.model_fields
        if name not in UNGATED_FIELD_NAMES and data[name]
    }


def test_active_item_with_required_fields_is_valid(
    merged_person: MergedPerson,
) -> None:
    data = merged_person.model_dump()

    assert MergedPerson.model_validate(data).model_dump() == data


def test_merged_items_are_frozen_and_copies_are_gated(
    merged_person: MergedPerson,
) -> None:
    person = MergedPerson.model_validate(merged_person.model_dump())

    with pytest.raises(ValidationError, match="frozen_instance"):
        person.supersededBy = person.identifier  # type: ignore[misc]

    with pytest.raises(ValidationError, match="superseded_value"):
        person.model_copy_validated(update={"supersededBy": "supersededBy8901234567"})

    with pytest.raises(ValidationError, match="too_short"):
        person.model_copy_validated(update={"fullName": []})


def test_superseded_item_cannot_supersede_itself() -> None:
    with pytest.raises(ValidationError) as error:
        MergedPerson.model_validate(
            {
                "identifier": "someIdentifier1234567",
                "supersededBy": "someIdentifier1234567",
            }
        )

    assert get_error_types_by_field(error.value) == {
        "supersededBy": "superseded_by_self"
    }


class _RequiredThingLists(PydanticBaseModel):
    tags: Annotated[list[str], Field(min_length=2)]


class _SparseThingLists(PydanticBaseModel):
    tags: list[str] = []


class BaseThing(_RequiredThingLists):
    pass


class MergedThing(_SparseThingLists, BaseThing, MergedItem):
    identifier: str
    supersededBy: str | None = None


def test_active_item_errors_use_required_field_constraints() -> None:
    assert MergedThing.requiredUnlessSuperseded == ("tags",)
    assert MergedThing(identifier="thing", tags=["a", "b"]).tags == ["a", "b"]

    with pytest.raises(ValidationError) as error:
        MergedThing(identifier="thing", tags=["a"])

    assert [(e["loc"], e["type"], e["ctx"]) for e in error.value.errors()] == [
        (
            ("tags",),
            "too_short",
            {"field_type": "List", "min_length": 2, "actual_length": 1},
        )
    ]
