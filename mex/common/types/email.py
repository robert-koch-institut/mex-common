from typing import Any

from pydantic.networks import EmailStr, pretty_email_regex


class Email(EmailStr):
    """Email address of a person, organization or other entity."""

    @classmethod
    def __modify_schema__(cls, field_schema: dict[str, Any]) -> None:
        """Mutate the field schema for email strings."""
        field_schema.update(
            type="string", format="email", pattern=pretty_email_regex.pattern
        )
