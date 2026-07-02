from mex.common.assets import FilesystemAssetsConnector, register_assets_connector
from mex.common.identity.backend_api import BackendApiIdentityProvider
from mex.common.identity.memory import MemoryIdentityProvider
from mex.common.identity.registry import register_provider
from mex.common.types import AssetsConnectorType, IdentityProvider

# register the default providers shipped with mex-common
register_provider(IdentityProvider.MEMORY, MemoryIdentityProvider)
register_provider(IdentityProvider.BACKEND, BackendApiIdentityProvider)
register_assets_connector(AssetsConnectorType.FILESYSTEM, FilesystemAssetsConnector)
