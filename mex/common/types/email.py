from typing import Any, Type

from pydantic.networks import EmailStr, pretty_email_regex
from pydantic_core import core_schema


class Email(EmailStr):
    """Email address of a person, organization or other entity."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source: Type[Any]) -> core_schema.CoreSchema:
        return core_schema.general_after_validator_function(
            cls._validate,
            {
                # "title": cls.__name__,
                "type": "str",
                # "format": "email",
                "pattern": pretty_email_regex.pattern,
            },
        )
