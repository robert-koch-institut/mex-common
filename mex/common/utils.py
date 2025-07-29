from collections.abc import Callable, Container, Generator, Iterable, Iterator, Mapping
from dataclasses import dataclass
from functools import lru_cache
from itertools import zip_longest
from random import random
from time import sleep
from types import NoneType, UnionType
from typing import Annotated, Any, Literal, TypeVar, Union, get_args, get_origin

from pydantic import BaseModel, TypeAdapter, ValidationError

T = TypeVar("T")


@dataclass
class GenericFieldInfo:
    """Abstraction class for unifying `FieldInfo` and `ComputedFieldInfo` objects."""

    alias: str | None
    annotation: type[Any] | None
    frozen: bool


def contains_any(base: Container[T], tokens: Iterable[T]) -> bool:
    """Check if a given base contains any of the given tokens."""
    return any(token in base for token in tokens)


def any_contains_any(bases: Iterable[Container[T] | None], tokens: Iterable[T]) -> bool:
    """Check if any of the given bases contains any of the given tokens."""
    for base in bases:
        if base is None:
            continue
        for token in tokens:
            if token in base:
                return True
    return False


def contains_only_types(field: GenericFieldInfo, *types: type) -> bool:
    """Return whether a `field` is annotated as one of the given `types`.

    Unions, lists and type annotations are checked for their inner types and only the
    non-`NoneType` types are considered for the type-check.

    Args:
        field: A `GenericFieldInfo` instance
        types: Types to look for in the field's annotation

    Returns:
        Whether the field contains any of the given types
    """
    if inner_types := list(get_inner_types(field.annotation, include_none=False)):
        return all(inner_type in types for inner_type in inner_types)
    return False


def contains_any_types(field: GenericFieldInfo, *types: type) -> bool:
    """Return whether a `field` is annotated as any of the given `types`.

    Unions, lists and type annotations are checked for their inner types and only the
    non-`NoneType` types are considered for the type-check.

    Args:
        field: A `GenericFieldInfo` instance
        types: Types to look for in the field's annotation

    Returns:
        Whether the field contains any of the given types
    """
    if inner_types := list(get_inner_types(field.annotation, include_none=False)):
        return any(inner_type in types for inner_type in inner_types)
    return False


def get_inner_types(
    annotation: Any,  # noqa: ANN401
    include_none: bool = True,  # noqa: FBT001, FBT002
    unpack_list: bool = True,  # noqa: FBT001, FBT002
    unpack_literal: bool = True,  # noqa: FBT001, FBT002
) -> Generator[type, None, None]:
    """Recursively yield all inner types from a given type annotation.

    Args:
        annotation: The type annotation to process
        include_none: Whether to include NoneTypes in output
        unpack_list: Whether to unpack list types
        unpack_literal: Whether to unpack Literal types

    Returns:
        All inner types found within the annotation
    """
    # Check whether to unpack lists in addition to annotations and unions
    types_to_unpack = [Annotated, Union, UnionType] + ([list] if unpack_list else [])

    # Get the unsubscripted version of the given type annotation
    origin_type = get_origin(annotation)

    # If the origin should be unpacked
    if origin_type in types_to_unpack:
        for inner_type in get_args(annotation):
            # Recursively process each inner type
            yield from get_inner_types(
                inner_type, include_none, unpack_list, unpack_literal
            )

    # Handle Literal types based on the unpack_literal flag
    elif origin_type is Literal:
        if unpack_literal:
            yield origin_type  # Return Literal if unpacking is allowed
        else:
            yield annotation  # Return the full annotation if not

    # Yield the origin type if present
    elif origin_type is not None:
        yield origin_type

    # Yield the annotation if it is valid type, that isn't NoneType
    elif isinstance(annotation, type) and annotation is not NoneType:
        yield annotation

    # Optionally yield none types
    elif include_none and annotation in (None, NoneType):
        yield NoneType


@lru_cache(maxsize=4048)
def get_all_fields(model: type[BaseModel]) -> dict[str, GenericFieldInfo]:
    """Return a combined dict of defined and computed fields of a given model.

    This function combines both regular model fields and computed fields into a
    single dictionary using the GenericFieldInfo abstraction. Results are cached
    for performance.

    Args:
        model: The Pydantic model class to extract fields from.

    Returns:
        Dictionary mapping field names to GenericFieldInfo objects for all fields
        (both regular and computed) in the model.
    """
    return {
        **{
            name: GenericFieldInfo(
                alias=info.alias,
                annotation=info.annotation,
                frozen=bool(info.frozen),
            )
            for name, info in model.model_fields.items()
        },
        **{
            name: GenericFieldInfo(
                alias=info.alias,
                annotation=info.return_type,
                frozen=True,
            )
            for name, info in model.model_computed_fields.items()
        },
    }


@lru_cache(maxsize=4048)
def get_alias_lookup(model: type[BaseModel]) -> dict[str, str]:
    """Build a cached mapping from field alias to field names.

    Creates a dictionary that maps field aliases (or field names if no alias exists)
    back to the actual field names. This is useful for resolving field references
    when working with serialized data that may use aliases.

    Args:
        model: The Pydantic model class to build the alias lookup for.

    Returns:
        Dictionary mapping field aliases (or names) to actual field names.
    """
    return {
        field_info.alias or field_name: field_name
        for field_name, field_info in get_all_fields(model).items()
    }


@lru_cache(maxsize=4048)
def get_list_field_names(model: type[BaseModel]) -> list[str]:
    """Build a cached list of fields that look like lists.

    Analyzes the model's field annotations to identify fields that are list types.
    This includes direct list annotations and list types within unions.

    Args:
        model: The Pydantic model class to analyze.

    Returns:
        List of field names that have list-like type annotations.
    """
    field_names = []
    for field_name, field_info in get_all_fields(model).items():
        field_types = get_inner_types(field_info.annotation, unpack_list=False)
        if any(
            isinstance(field_type, type) and issubclass(field_type, list)
            for field_type in field_types
        ):
            field_names.append(field_name)
    return field_names


@lru_cache(maxsize=4048)
def get_field_names_allowing_none(model: type[BaseModel]) -> list[str]:
    """Build a cached list of fields that can be set to None.

    Tests each field's annotation by attempting to validate None against it.
    Fields that accept None without raising a ValidationError are considered
    nullable fields.

    Args:
        model: The Pydantic model class to analyze.

    Returns:
        List of field names that accept None as a valid value.
    """
    field_names: list[str] = []
    for field_name, field_info in get_all_fields(model).items():
        validator: TypeAdapter[Any] = TypeAdapter(field_info.annotation)
        try:
            validator.validate_python(None)
        except ValidationError:
            continue
        field_names.append(field_name)
    return field_names


def group_fields_by_class_name(
    model_classes_by_name: Mapping[str, type[BaseModel]],
    predicate: Callable[[GenericFieldInfo], bool],
) -> dict[str, list[str]]:
    """Group the field names by model class and filter them by the given predicate.

    For each model class, extracts all fields and applies the predicate function
    to filter them. Returns a mapping from class names to lists of field names
    that satisfy the predicate condition.

    Args:
        model_classes_by_name: Map from class names to model classes.
        predicate: Function to filter the fields of the classes by.

    Returns:
        Dictionary mapping class names to a list of field names filtered by `predicate`.
    """
    return {
        name: sorted(
            {
                field_name
                for field_name, field_info in get_all_fields(cls).items()
                if predicate(field_info)
            }
        )
        for name, cls in model_classes_by_name.items()
    }


def grouper(chunk_size: int, iterable: Iterable[T]) -> Iterator[Iterable[T | None]]:
    """Collect data into fixed-length chunks or blocks.

    Groups items from an iterable into fixed-size chunks. The last chunk may be
    padded with None values if the total number of items is not evenly divisible
    by the chunk size.

    Args:
        chunk_size: The size of each chunk.
        iterable: The iterable to group into chunks.

    Returns:
        Iterator of iterables, each containing chunk_size items (with None padding
        for the final chunk if necessary).
    """
    # https://docs.python.org/3.9/library/itertools.html#itertools-recipes
    args = [iter(iterable)] * chunk_size
    return zip_longest(*args, fillvalue=None)


def jitter_sleep(min_seconds: float, jitter_seconds: float) -> None:
    """Sleep a random amount of seconds within the given parameters.

    Args:
        min_seconds: The minimum time to sleep
        jitter_seconds: The variable sleep time added to the minimum
    """
    sleep(min_seconds + random() * jitter_seconds)  # noqa: S311


def ensure_list(values: list[T] | T | None) -> list[T]:
    """Put objects in lists, replace None with an empty list and return lists as is."""
    if values is None:
        return []
    if isinstance(values, list):
        return values
    return [values]
