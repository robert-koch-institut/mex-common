from mex.common.cli import entrypoint
from mex.common.mapping.schema import entity_filter_schemas, mapping_schemas
from mex.common.mapping.template import entity_filter_templates, mapping_templates
from mex.common.settings import BaseSettings


@entrypoint(BaseSettings)
def generate_mapping_schemas_and_templates() -> None:
    """Generate schemas and templates for mappings and entity filters."""
    mapping_schemas()
    entity_filter_schemas()
    mapping_templates()
    entity_filter_templates()
