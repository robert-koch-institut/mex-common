import re
from collections.abc import Callable, Container, Generator, Iterable, Iterator, Mapping
from functools import cache
from itertools import zip_longest
from random import random
from time import sleep
from types import NoneType, UnionType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

if TYPE_CHECKING:  # pragma: no cover
    from mex.common.models import GenericFieldInfo
    from mex.common.models.base.model import BaseModel

T = TypeVar("T")


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


def contains_only_types(field: "GenericFieldInfo", *types: type) -> bool:
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


def get_inner_types(
    annotation: Any,
    include_none: bool = True,
    unpack_list: bool = True,
    unpack_literal: bool = True,
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


def group_fields_by_class_name(
    model_classes_by_name: Mapping[str, type["BaseModel"]],
    predicate: Callable[["GenericFieldInfo"], bool],
) -> dict[str, list[str]]:
    """Group the field names by model class and filter them by the given predicate.

    Args:
        model_classes_by_name: Map from class names to model classes
        predicate: Function to filter the fields of the classes by

    Returns:
        Dictionary mapping class names to a list of field names filtered by `predicate`
    """
    return {
        name: sorted(
            {
                field_name
                for field_name, field_info in cls.get_all_fields().items()
                if predicate(field_info)
            }
        )
        for name, cls in model_classes_by_name.items()
    }


@cache
def normalize(string: str) -> str:
    """Normalize the given string to lowercase, numerals and single spaces."""
    return " ".join(re.sub(r"[^a-z0-9]", " ", string.lower()).split())


def grouper(chunk_size: int, iterable: Iterable[T]) -> Iterator[Iterable[T | None]]:
    """Collect data into fixed-length chunks or blocks."""
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
