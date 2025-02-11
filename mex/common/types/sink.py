from enum import Enum


class Sink(Enum):
    """Configuration to choose where to send outbound data."""

    BACKEND = "backend"
    GRAPH = "graph"
    NDJSON = "ndjson"
    S3 = "s3"
