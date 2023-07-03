from enum import Enum


class Sink(Enum):
    """Configuration enum to choose where to funnel inbound data."""

    BACKEND = "backend"
    GRAPH = "graph"
    NDJSON = "ndjson"
    PUBLIC = "public"
