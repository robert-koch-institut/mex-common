import json
from base64 import b64encode
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Optional, TypeVar, Union

from pydantic import AnyUrl, Field, SecretStr
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic_settings.sources import ENV_FILE_SENTINEL, DotenvType, EnvSettingsSource

from mex.common.identity.types import IdentityProvider
from mex.common.sinks import Sink
from mex.common.transform import MExEncoder
from mex.common.types import AssetsPath, WorkPath

SettingsType = TypeVar("SettingsType", bound="BaseSettings")
SettingsContext: ContextVar[Optional["BaseSettings"]] = ContextVar(
    "SettingsContext", default=None
)


class BaseSettings(PydanticBaseSettings):
    """Common settings definition class."""

    model_config = SettingsConfigDict(
        populate_by_name=True,
        env_prefix="mex_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
        validate_assignment=True,
    )

    def __init__(
        self,
        _env_file: Optional[DotenvType] = ENV_FILE_SENTINEL,
        _env_file_encoding: Optional[str] = None,
        _env_nested_delimiter: Optional[str] = None,
        _secrets_dir: str | Path | None = None,
        **values: Any,
    ) -> None:
        """Construct a new settings instance.

        After building from regular settings sources, we look for a configured
        `assets_dir` and then check that folder for a dotenv file as well.
        Because of this dependency from one setting source to another, sadly
        we cannot use `Config.customise_sources`.
        """
        settings_wo_assets_env_file = self._settings_build_values(
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
        if settings is None:
            settings = cls.model_validate({})
            SettingsContext.set(settings)
        if isinstance(settings, cls):
            return settings
        raise RuntimeError(f"Requested {cls} but already loaded {type(settings)}")

    # Note: We need to hardcode the environment variable names for base settings here,
    # otherwise their prefix will get overwritten with those of a specific subclass.

    debug: bool = Field(
        False,
        alias="pdb",
        description="Enable debug mode.",
        validation_alias="MEX_DEBUG",
    )
    sink: list[Sink] = Field(
        [Sink.NDJSON, Sink.NDJSON],
        description=(
            "Where to send data that is extracted or ingested. Defaults to writing "
            "ndjson files, but can be set to backend or public APIs or to graph db."
        ),
        validation_alias="MEX_SINK",
    )
    assets_dir: Path = Field(
        Path.cwd() / "assets",
        description=(
            "Path to directory that contains input files treated as read-only, "
            "looks for a folder named `assets` in the current directory by default."
        ),
        validation_alias="MEX_ASSETS_DIR",
    )
    work_dir: Path = Field(
        Path.cwd(),
        description=(
            "Path to directory that stores generated and temporary files. "
            "Defaults to the current working directory."
        ),
        validation_alias="MEX_WORK_DIR",
    )
    identity_provider: IdentityProvider = Field(
        IdentityProvider.DUMMY,
        description="Provider to assign stableTargetIds to new model instances.",
        validation_alias="MEX_IDENTITY_PROVIDER",
    )
    backend_api_url: AnyUrl = Field(
        "http://localhost:8080/",
        description="MEx backend API url.",
        validation_alias="MEX_BACKEND_API_URL",
    )
    verify_session: Union[bool, AssetsPath] = Field(
        True,
        description=(
            "Either a boolean that controls whether we verify the server's TLS "
            "certificate, or a path to a CA bundle to use. If a path is given, it can "
            "be either absolute or relative to the `assets_dir`. Defaults to True."
        ),
        validation_alias="MEX_VERIFY_SESSION",
    )
    sqlite_path: WorkPath = Field(
        "mex.db",
        alias="db",
        description=(
            "Path to the MEx sqlite database, absolute or relative to `work_dir`."
        ),
        validation_alias="MEX_SQLITE_PATH",
    )
    public_api_url: AnyUrl = Field(
        "http://localhost:53000/",
        description="MEx public API url.",
        validation_alias="MEX_PUBLIC_API_URL",
    )
    public_api_token_provider: AnyUrl = Field(
        "http://localhost:53000/api/v0/oauth/token",
        description="URL of the JSON Web Token provider for the public API.",
        validation_alias="MEX_PUBLIC_API_TOKEN_PROVIDER",
    )
    public_api_token_payload: SecretStr = Field(
        SecretStr(b64encode(b"payload").decode()),
        description=(
            "Base64-encoded payload to send when requesting a JWT for the public API."
        ),
        validation_alias="MEX_PUBLIC_API_TOKEN_PAYLOAD",
    )
    public_api_verify_session: Union[bool, AssetsPath] = Field(
        True,
        description=(
            "Public API-specific session verification setting, "
            "see `verify_session` for possible values."
        ),
        validation_alias="MEX_PUBLIC_API_VERIFY_SESSION",
    )
    organigram_path: AssetsPath = Field(
        "raw-data/organigram/organizational_units.json",
        description=(
            "Path to the JSON file describing the organizational units, "
            "absolute path or relative to `assets_dir`."
        ),
        validation_alias="MEX_ORGANIGRAM_PATH",
    )
    ldap_url: SecretStr = Field(
        SecretStr("ldap://user:pw@ldap:636"),
        description="LDAP server for person queries with authentication credentials.",
        validation_alias="MEX_LDAP_URL",
    )
    wiki_api_url: AnyUrl = Field(
        "https://wikidata/",
        description="URL of Wikidata API",
        validation_alias="MEX_WIKI_API_URL",
    )
    wiki_query_service_url: AnyUrl = Field(
        "https://wikidata/",
        description="URL of Wikidata query service",
        validation_alias="MEX_WIKI_QUERY_SERVICE_URL",
    )

    def text(self) -> str:
        """Dump the current settings into a readable table."""
        dict_ = self.model_dump()
        indent = max(len(key) for key in dict_)
        return "\n".join(
            [
                f"{key.ljust(indent)} "
                f"{', '.join(str(v) for v in value) if isinstance(value, list) else value}"
                for key, value in dict_.items()
            ]
        )

    @classmethod
    def get_env_name(cls, name: str) -> str:
        """Get the name of the environment variable for field with given name."""
        field = cls.model_fields[name]
        env_settings = EnvSettingsSource(
            cls,
            case_sensitive=cls.model_config.get("case_sensitive", False),
            env_prefix=cls.model_config.get("env_prefix", ""),
        )
        env_info = env_settings._extract_field_info(field, name)
        env_name = env_info[0][1].upper()
        return env_name

    def env(self) -> dict[str, str]:
        """Dump the current settings as a mapping of environment variables."""
        return {
            self.get_env_name(key): json.dumps(value, cls=MExEncoder).strip('"')
            for key, value in self.model_dump().items()
            if value not in (None, [], {})
        }

    def env_text(self) -> str:
        """Dump the current settings as an .env-file compatible text."""
        return "\n".join(
            '{}="{}"'.format(key, value.replace('"', '\\"'))
            for key, value in sorted(self.env().items())
        )
