from pathlib import Path
from typing import Any, Self, cast

from pydantic import AnyUrl, Field, SecretStr, model_validator
from pydantic import BaseModel as PydanticBaseModel
from pydantic_core import Url
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict
from pydantic_settings.sources import ENV_FILE_SENTINEL, DotenvType, EnvSettingsSource

from mex.common.context import SingleSingletonStore
from mex.common.types import AssetsPath, IdentityProvider, Sink, WorkPath

SETTINGS_STORE = SingleSingletonStore["BaseSettings"]()


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

    model_config = SettingsConfigDict(
        populate_by_name=True,
        env_prefix="mex_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        validate_default=True,
        validate_assignment=True,
    )

    def __init__(
        self,
        _env_file: DotenvType | None = ENV_FILE_SENTINEL,
        _env_file_encoding: str | None = None,
        _env_nested_delimiter: str | None = None,
        _secrets_dir: str | Path | None = None,
        **values: Any,  # noqa: ANN401
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
        if assets_dir := settings_wo_assets_env_file.get("MEX_ASSETS_DIR"):
            _env_file = Path(assets_dir, ".env")
        super().__init__(
            _env_file=_env_file,
            _env_file_encoding=_env_file_encoding,
            _env_nested_delimiter=_env_nested_delimiter,
            _secrets_dir=_secrets_dir,
            **values,
        )

    @classmethod
    def get(cls) -> Self:
        """Get the current settings instance from singleton store.

        Returns:
            An instance of BaseSettings or a subclass thereof
        """
        return cast("Self", SETTINGS_STORE.load(cls))

    # Note: We need to hardcode the environment variable names for base settings here,
    # otherwise their prefix will get overwritten with those of a specific subclass.

    debug: bool = Field(
        False,  # noqa: FBT003
        alias="pdb",
        description="Jump into post-mortem debugging after any uncaught exception.",
        validation_alias="MEX_DEBUG",
    )
    sink: list[Sink] = Field(
        [Sink.NDJSON],
        description=(
            "Where to send data that is extracted or ingested. Defaults to writing "
            "ndjson files, but can be configured to push to the backend or the graph."
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
        IdentityProvider.MEMORY,
        description="Provider to assign identifiers to new model instances.",
        validation_alias="MEX_IDENTITY_PROVIDER",
    )
    backend_api_url: AnyUrl = Field(
        Url("http://localhost:8080/"),
        description="MEx backend API url.",
        validation_alias="MEX_BACKEND_API_URL",
    )
    backend_api_key: SecretStr = Field(
        SecretStr("dummy_write_key"),
        description="Backend API key with write access to call POST/PUT endpoints",
        validation_alias="MEX_BACKEND_API_KEY",
    )
    backend_api_parallelization: int = Field(
        1,
        description=(
            "How many simultaneous threads may spin up to load data into the backend."
        ),
        validation_alias="MEX_BACKEND_API_PARALLELIZATION",
    )
    backend_api_chunk_size: int = Field(
        25,
        description="How many items to load into the backend in one chunk.",
        validation_alias="MEX_BACKEND_API_CHUNK_SIZE",
    )
    verify_session: bool | AssetsPath = Field(
        True,  # noqa: FBT003
        description=(
            "Either a boolean that controls whether we verify the server's TLS "
            "certificate, or a path to a CA bundle to use. If a path is given, it can "
            "be either absolute or relative to the `assets_dir`. Defaults to True."
        ),
        validation_alias="MEX_VERIFY_SESSION",
    )
    organigram_path: AssetsPath = Field(
        AssetsPath("raw-data/organigram/organizational_units.json"),
        description=(
            "Path to the JSON file describing the organizational units, "
            "absolute path or relative to `assets_dir`."
        ),
        validation_alias="MEX_ORGANIGRAM_PATH",
    )
    primary_sources_path: AssetsPath = Field(
        AssetsPath("raw-data/primary-sources/primary-sources.json"),
        description=(
            "Path to the JSON file describing the primary sources, "
            "absolute path or relative to `assets_dir`."
        ),
        validation_alias="MEX_PRIMARY_SOURCES_PATH",
    )
    ldap_url: SecretStr = Field(
        SecretStr("ldap://user:pw@ldap:636"),
        description="LDAP server for person queries with authentication credentials. "
        "Must follow format `ldap://user:pw@host:port`, where "
        "`user` is the username, and "
        "`pw` is the password for authenticating against ldap, "
        "`host` is the url of the ldap server, and "
        "`port` is the port of the ldap server.",
        validation_alias="MEX_LDAP_URL",
    )
    ldap_search_base: str = Field(
        "DC=rki,DC=local",
        description="Search base for the ldap connector.",
        validation_alias="MEX_LDAP_SEARCH_BASE",
    )
    wiki_api_url: AnyUrl = Field(
        Url("http://wikidata/"),
        description="URL of the Wikidata API used to resolve an ID to an organization.",
        validation_alias="MEX_WIKI_API_URL",
    )
    mex_web_user_agent: str = Field(
        "rki/mex",
        description="User agent is sent in request headers to external services.",
        validation_alias="MEX_WEB_USER_AGENT",
    )
    orcid_api_url: AnyUrl = Field(
        Url("https://orcid"),
        description="URL of orcid api.",
        validation_alias="MEX_ORCID_API_URL",
    )

    def text(self) -> str:
        """Dump the current settings into a readable table.

        Returns:
            Formatted string with all settings key-value pairs.
        """
        dict_ = self.model_dump()
        indent = max(len(key) for key in dict_)
        return "\n".join(
            [
                f"{key.ljust(indent)} "
                f"{', '.join(str(v) for v in val) if isinstance(val, list) else val}"
                for key, val in dict_.items()
            ]
        )

    @classmethod
    def get_env_name(cls, name: str) -> str:
        """Get the name of the environment variable for field with given name.

        Resolves the actual environment variable name that would be used for a
        given field, taking into account case sensitivity and environment prefix
        configuration.

        Args:
            name: The field name to get the environment variable name for.

        Returns:
            The uppercase environment variable name that maps to the field.
        """
        field = cls.model_fields[name]
        env_settings = EnvSettingsSource(
            cls,
            case_sensitive=cls.model_config.get("case_sensitive", False),
            env_prefix=cls.model_config.get("env_prefix", ""),
        )
        env_info = env_settings._extract_field_info(field, name)  # noqa: SLF001
        return env_info[0][1].upper()

    @model_validator(mode="after")
    def resolve_paths(self) -> Self:
        """Resolve AssetPath and WorkPath."""

        def _resolve(model: PydanticBaseModel, _name: str) -> None:
            value = getattr(model, _name)
            if isinstance(value, AssetsPath) and value.is_relative():
                setattr(model, _name, self.assets_dir.resolve() / value)
            elif isinstance(value, WorkPath) and value.is_relative():
                setattr(model, _name, self.work_dir.resolve() / value)
            elif isinstance(value, PydanticBaseModel):
                for sub_model_field_name in value.model_fields:
                    _resolve(value, sub_model_field_name)

        for name in self.model_fields:
            _resolve(self, name)
        return self
