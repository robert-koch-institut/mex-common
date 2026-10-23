from typing import Annotated, Any, ClassVar, Self, cast

from pydantic import BaseModel as PydanticBaseModel
from pydantic import GetJsonSchemaHandler, TypeAdapter, model_validator
from pydantic.fields import FieldInfo
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
    in `requiredUnlessSuperseded`. Active items validate these fields against their
    original, required definition, including all of its constraints.
    """

    requiredUnlessSuperseded: ClassVar[tuple[str, ...]] = ()
    _required_field_adapters: ClassVar[dict[str, TypeAdapter[Any]]] = {}

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:  # noqa: ANN401
        """Collect the fields that are only required while not superseded."""
        super().__pydantic_init_subclass__(**kwargs)
        required_field_infos = {
            field_name: required_field_info
            for field_name, field_info in sorted(cls.model_fields.items())
            if not field_info.is_required()
            and (required_field_info := cls._get_required_field_info(field_name))
        }
        cls.requiredUnlessSuperseded = tuple(required_field_infos)
        cls._required_field_adapters = {
            field_name: TypeAdapter(
                cast("Any", Annotated[field_info.annotation, field_info])
            )
            for field_name, field_info in required_field_infos.items()
        }

    @classmethod
    def _get_required_field_info(cls, field_name: str) -> FieldInfo | None:
        """Return the first required definition of a field on any base model."""
        for base in cls.__mro__[1:]:
            if (
                issubclass(base, PydanticBaseModel)
                and (field_info := base.model_fields.get(field_name))
                and field_info.is_required()
            ):
                return field_info
        return None

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
        """Return errors for required fields that are not valid on an active item."""
        errors: list[InitErrorDetails] = []
        for field_name, adapter in self._required_field_adapters.items():
            value = getattr(self, field_name)
            if value is None:
                errors.append(
                    InitErrorDetails(type="missing", loc=(field_name,), input=value)
                )
                continue
            try:
                adapter.validate_python(value)
            except ValidationError as error:
                for details in error.errors():
                    init_details = InitErrorDetails(
                        type=details["type"],
                        loc=(field_name, *details["loc"]),
                        input=details["input"],
                    )
                    if "ctx" in details:
                        init_details["ctx"] = details["ctx"]
                    errors.append(init_details)
        return errors

    def _get_superseded_item_errors(self) -> list[InitErrorDetails]:
        """Return errors for fields with non-default values on a superseded item."""
        errors: list[InitErrorDetails] = []
        if (superseded_by := getattr(self, "supersededBy", None)) == getattr(
            self, "identifier", None
        ):
            errors.append(
                InitErrorDetails(
                    type=PydanticCustomError(
                        "superseded_by_self",
                        "Items cannot be superseded by themselves",
                    ),
                    loc=("supersededBy",),
                    input=superseded_by,
                )
            )
        return errors + [
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
