from mex.common.assets import FilesystemAssetsConnector, register_assets_connector
from mex.common.identity import (
    BackendApiIdentityProvider,
    MemoryIdentityProvider,
    register_provider,
)
from mex.common.sinks import BackendApiSink, NdjsonSink, register_sink
from mex.common.types import AssetsConnectorType, IdentityProvider, Sink

# register the default implementations shipped with mex-common
register_assets_connector(AssetsConnectorType.FILESYSTEM, FilesystemAssetsConnector)
register_provider(IdentityProvider.BACKEND, BackendApiIdentityProvider)
register_provider(IdentityProvider.MEMORY, MemoryIdentityProvider)
register_sink(Sink.BACKEND, BackendApiSink)
register_sink(Sink.NDJSON, NdjsonSink)
