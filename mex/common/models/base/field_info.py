from dataclasses import dataclass
from typing import Any


@dataclass
class GenericFieldInfo:
    """Abstraction class for unifying `FieldInfo` and `ComputedFieldInfo` objects."""

    alias: str | None
    annotation: type[Any] | None
    frozen: bool
