import json
from base64 import b64encode
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Optional, TypeVar, Union

from pydantic import AnyUrl, Extra, Field, SecretStr
from pydantic import BaseSettings as PydanticBaseSettings
from pydantic.env_settings import DotenvType, env_file_sentinel
from pydantic.typing import StrPath

from mex.common.identity.types import IdentityProvider
from mex.common.sinks.types import Sink
from mex.common.transform import MExEncoder
from mex.common.types import AssetsPath

SettingsType = TypeVar("SettingsType", bound="BaseSettings")
SettingsContext: ContextVar[Optional["BaseSettings"]] = ContextVar(
    "SettingsContext", default=None
)


class BaseSettings(PydanticBaseSettings):
    """Common settings definition class.

    Settings are accessed through a singleton instance of a pydantic settings class.
    The singleton instance can be loaded lazily by calling `BaseSettings.get()`.

    The base settings should only contain options, that are used by common code.
    To add more configuration options for a specific subsystem, create a new subclass
    and define the required fields there. To load a singleton for that subclass,
    simply call `SubsystemSettings.get()`.

    All configuration options should have a speaking name and a clear description.
    The defaults should be set to a value that works with unit tests and must not
    contain any secrets or live URLs that would break unit test isolation.
    """

    class Config:
        allow_population_by_field_name = True
        env_prefix = "mex_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = Extra.ignore
        validate_all = True
        validate_assignment = True

    def __init__(
        self,
        _env_file: DotenvType | None = env_file_sentinel,
        _env_file_encoding: str | None = None,
        _env_nested_delimiter: str | None = None,
        _secrets_dir: StrPath | None = None,
        **values: Any,
    ) -> None:
        """Construct a new settings instance.

        After building from regular settings sources, we look for a configured
        `assets_dir` and then check that folder for a dotenv file as well.
        Because of this dependency from one setting source to another, sadly
        we cannot use `Config.customise_sources`.
        """
        settings_wo_assets_env_file = self._build_values(
            values,
            _env_file=_env_file,
            _env_file_encoding=_env_file_encoding,
            _env_nested_delimiter=_env_nested_delimiter,
            _secrets_dir=_secrets_dir,
        )
        if assets_dir := settings_wo_assets_env_file.get("assets_dir"):
            _env_file = Path(assets_dir, ".env")
        super().__init__(
            _env_file=_env_file,
            _env_file_encoding=_env_file_encoding,
            _env_nested_delimiter=_env_nested_delimiter,
            _secrets_dir=_secrets_dir,
            **values,
        )

    @classmethod
    def get(cls: type[SettingsType]) -> SettingsType:
        """Get the current settings instance from the active context.

        Returns:
            Settings: An instance of Settings or a subclass thereof
        """
        settings = SettingsContext.get()
        if isinstance(settings, cls):
            return settings
        if settings is None:
            base = {}
        elif issubclass(cls, type(settings)):
            base = settings.dict(exclude_unset=True)
        else:
            raise RuntimeError(
                f"Requested {cls.__name__} but already loaded {type(settings).__name__}"
            )
        settings = cls.parse_obj(base)
        SettingsContext.set(settings)
        return settings

    # Note: We need to hardcode the environment variable names for base settings here,
    # otherwise their prefix will get overwritten with those of a specific subclass.

    debug: bool = Field(
        False,
        alias="pdb",
        description="Jump into post-mortem debugging after any uncaught exception.",
        env="MEX_DEBUG",
    )
    sink: list[Sink] = Field(
        [Sink.NDJSON],
        description=(
            "Where to send data that is extracted or ingested. Defaults to writing "
            "ndjson files, but can be set to backend or public APIs or to graph db."
        ),
        env="MEX_SINK",
    )
    assets_dir: Path = Field(
        Path.cwd() / "assets",
        description=(
            "Path to directory that contains input files treated as read-only, "
            "looks for a folder named `assets` in the current directory by default."
        ),
        env="MEX_ASSETS_DIR",
    )
    work_dir: Path = Field(
        Path.cwd(),
        description=(
            "Path to directory that stores generated and temporary files. "
            "Defaults to the current working directory."
        ),
        env="MEX_WORK_DIR",
    )
    identity_provider: IdentityProvider = Field(
        IdentityProvider.MEMORY,
        description="Provider to assign stableTargetIds to new model instances.",
        env="MEX_IDENTITY_PROVIDER",
    )
    backend_api_url: AnyUrl = Field(
        "http://localhost:8080/",
        description="MEx backend API url.",
        env="MEX_BACKEND_API_URL",
    )
    backend_api_key: SecretStr = Field(
        SecretStr("dummy_write_key"),
        description="Backend API key with write access to call POST/PUT endpoints",
        env="MEX_BACKEND_API_KEY",
    )
    verify_session: Union[bool, AssetsPath] = Field(
        True,
        description=(
            "Either a boolean that controls whether we verify the server's TLS "
            "certificate, or a path to a CA bundle to use. If a path is given, it can "
            "be either absolute or relative to the `assets_dir`. Defaults to True."
        ),
        env="MEX_VERIFY_SESSION",
    )
    public_api_url: AnyUrl = Field(
        "http://localhost:53000/",
        description="MEx public API url.",
        env="MEX_PUBLIC_API_URL",
    )
    public_api_token_provider: AnyUrl = Field(
        "http://localhost:53000/api/v0/oauth/token",
        description="URL of the JSON Web Token provider for the public API.",
        env="MEX_PUBLIC_API_TOKEN_PROVIDER",
    )
    public_api_token_payload: SecretStr = Field(
        SecretStr(b64encode(b"payload").decode()),
        description=(
            "Base64-encoded payload to send when requesting a JWT for the public API."
        ),
        env="MEX_PUBLIC_API_TOKEN_PAYLOAD",
    )
    public_api_verify_session: Union[bool, AssetsPath] = Field(
        True,
        description=(
            "Public API-specific session verification setting, "
            "see `verify_session` for possible values."
        ),
        env="MEX_PUBLIC_API_VERIFY_SESSION",
    )
    organigram_path: AssetsPath = Field(
        "raw-data/organigram/organizational_units.json",
        description=(
            "Path to the JSON file describing the organizational units, "
            "absolute path or relative to `assets_dir`."
        ),
        env="MEX_ORGANIGRAM_PATH",
    )
    primary_sources_path: AssetsPath = Field(
        "raw-data/primary-sources/primary-sources.json",
        description=(
            "Path to the JSON file describing the primary sources, "
            "absolute path or relative to `assets_dir`."
        ),
        env="MEX_PRIMARY_SOURCES_PATH",
    )
    ldap_url: SecretStr = Field(
        SecretStr("ldap://user:pw@ldap:636"),
        description="LDAP server for person queries with authentication credentials. "
        "Must follow format `ldap://user:pw@host:port`, where "
        "`user` is the username, and "
        "`pw` is the password for authenticating against ldap, "
        "`host` is the url of the ldap server, and "
        "`port` is the port of the ldap server.",
        env="MEX_LDAP_URL",
    )
    wiki_api_url: AnyUrl = Field(
        "https://wikidata/",
        description="URL of Wikidata API, this URL is used to send "
        "wikidata organizatizion ID to get all the info about the organization, "
        "which includes basic info, aliases, labels, descriptions, claims, and "
        "sitelinks",
        env="MEX_WIKI_API_URL",
    )
    wiki_query_service_url: AnyUrl = Field(
        "https://wikidata/",
        description="URL of Wikidata query service, this URL is to send organization "
        "name in plain text to wikidata and receive search results with wikidata "
        "organization ID",
        env="MEX_WIKI_QUERY_SERVICE_URL",
    )

    def text(self) -> str:
        """Dump the current settings into a readable table."""
        dict_ = self.dict()
        indent = max(len(key) for key in dict_)
        return "\n".join(
            [
                f"{key.ljust(indent)} "
                f"{', '.join(str(v) for v in val) if isinstance(val, list) else val}"
                for key, val in dict_.items()
            ]
        )

    def env(self) -> dict[str, str]:
        """Dump the current settings as a mapping of environment variables."""

        def get_env_name(key: str) -> str:
            return str(sorted(self.__fields__[key].field_info.extra["env_names"])[0])

        return {
            get_env_name(key).upper(): json.dumps(value, cls=MExEncoder).strip('"')
            for key, value in self.dict().items()
            if value not in (None, [], {})
        }

    def env_text(self) -> str:
        """Dump the current settings as an .env-file compatible text."""
        return "\n".join(
            '{}="{}"'.format(key, value.replace('"', '\\"'))
            for key, value in sorted(self.env().items())
        )
