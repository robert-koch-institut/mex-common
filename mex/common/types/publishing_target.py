from enum import Enum


class PublishingTarget(Enum):
    """Possible targets to which a merged item could be published."""

    INVENIO = "invenio"
    DATENKOMPASS = "datenkompass"
    TESTING = "testing"
