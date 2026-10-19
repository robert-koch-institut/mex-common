from typing import Any, ClassVar, Self

from pydantic import GetJsonSchemaHandler, model_validator
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import (
    CoreSchema,
    InitErrorDetails,
    PydanticCustomError,
    ValidationError,
)

from mex.common.models.base.model import BaseModel
from mex.common.transform import camel_to_split
from mex.common.utils import get_list_field_names

# fields that are exempt from the supersededBy gate
UNGATED_FIELD_NAMES = frozenset({"entityType", "identifier", "supersededBy"})


class MergedItem(
    BaseModel,
    extra="forbid",
    model_title_generator=lambda m: camel_to_split(m.__name__),
):
    """Base model for all merged item classes.

    Merged items have two valid shapes (see ADR-002 and ADR-004): active items, with
    `supersededBy` set to `None`, must populate every field their entity requires.
    Superseded items must leave every field except `identifier` and `supersededBy`
    at its default value.

    Subclasses relax their entity's required fields by listing its `_Sparse*` mixins
    before its `Base*` class, e.g. `MergedFoo(_SparseLists, BaseFoo, MergedItem)`.
    Every field that is required on a base class but relaxed this way is collected
    in `requiredUnlessSuperseded`, and is validated and documented accordingly.
    """

    requiredUnlessSuperseded: ClassVar[tuple[str, ...]] = ()

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Collect the fields that are only required while not superseded."""
        super().__pydantic_init_subclass__(**kwargs)
        cls.requiredUnlessSuperseded = tuple(
            sorted(
                field_name
                for field_name, field_info in cls.model_fields.items()
                if not field_info.is_required()
                and any(
                    (
                        inherited := vars(base)
                        .get("__pydantic_fields__", {})
                        .get(field_name)
                    )
                    is not None
                    and inherited.is_required()
                    for base in cls.__mro__[1:]
                )
            )
        )

    @model_validator(mode="after")
    def validate_supersession(self) -> Self:
        """Validate the fields of active and superseded merged items."""
        if getattr(self, "supersededBy", None) is None:
            errors = self._get_active_item_errors()
        else:
            errors = self._get_superseded_item_errors()
        if errors:
            raise ValidationError.from_exception_data(type(self).__name__, errors)
        return self

    def _get_active_item_errors(self) -> list[InitErrorDetails]:
        """Return errors for required fields that are not set on an active item."""
        errors: list[InitErrorDetails] = []
        for field_name in self.requiredUnlessSuperseded:
            value = getattr(self, field_name)
            if value is None:
                errors.append(
                    InitErrorDetails(type="missing", loc=(field_name,), input=value)
                )
            elif value == []:
                errors.append(
                    InitErrorDetails(
                        type="too_short",
                        loc=(field_name,),
                        input=value,
                        ctx={"field_type": "List", "min_length": 1, "actual_length": 0},
                    )
                )
        return errors

    def _get_superseded_item_errors(self) -> list[InitErrorDetails]:
        """Return errors for fields with non-default values on a superseded item."""
        return [
            InitErrorDetails(
                type=PydanticCustomError(
                    "superseded_value",
                    "Superseded items must keep the default value",
                ),
                loc=(field_name,),
                input=value,
            )
            for field_name, field_info in type(self).model_fields.items()
            if field_name not in UNGATED_FIELD_NAMES
            and (value := getattr(self, field_name))
            != field_info.get_default(call_default_factory=True)
        ]

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Add the supersededBy gate as an if/then/else conditional to the schema."""
        json_schema = handler.resolve_ref_schema(handler(core_schema))
        list_field_names = get_list_field_names(cls)
        aliases = {
            field_name: field_info.alias or field_name
            for field_name, field_info in cls.model_fields.items()
        }
        json_schema["allOf"] = [
            {
                "if": {"properties": {"supersededBy": {"type": "null"}}},
                "then": {
                    "properties": {
                        aliases[field_name]: {"minItems": 1}
                        if field_name in list_field_names
                        else {"not": {"type": "null"}}
                        for field_name in cls.requiredUnlessSuperseded
                    },
                    "required": [
                        aliases[field_name]
                        for field_name in cls.requiredUnlessSuperseded
                    ],
                },
                "else": {
                    "properties": {
                        aliases[field_name]: {"maxItems": 0}
                        if field_name in list_field_names
                        else {"type": "null"}
                        for field_name in cls.model_fields
                        if field_name not in UNGATED_FIELD_NAMES
                    }
                },
            }
        ]
        return json_schema
