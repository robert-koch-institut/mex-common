from enum import Enum


class PublishingStatus(Enum):
    """Status to prohibit merged items from being published."""

    INVALID_FOR_PUBLISHING = "invalid_for_publishing "
