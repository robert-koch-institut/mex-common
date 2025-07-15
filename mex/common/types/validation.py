from enum import Enum


class Validation(Enum):
    """Defines possible validation strategies."""

    STRICT = "strict"
    LENIENT = "lenient"
    IGNORE = "ignore"
