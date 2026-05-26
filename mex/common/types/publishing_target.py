from enum import StrEnum


class PublishingTarget(StrEnum):
    """Possible targets to which a merged item could be published."""

    INVENIO = "invenio"
    DATENKOMPASS = "datenkompass"
