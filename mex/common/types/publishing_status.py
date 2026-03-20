from enum import StrEnum


class PublishingStatus(StrEnum):
    """Status to prohibit merged items from being published."""

    INVALID_FOR_PUBLISHING = "invalid_for_publishing"
