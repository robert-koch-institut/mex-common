import re

import pytest

from mex.common.settings import BaseSettings, SettingsContext


def test_debug_setting() -> None:
    # Test settings can be instantiated as basic sanity check
    settings = BaseSettings(debug=True)  # type: ignore

    assert settings.debug is True


def test_settings_text() -> None:
    # Test settings can be converted to a ledigble multi-line paragraph
    settings = BaseSettings.get()
    text = settings.text()

    assert len(text.splitlines()) == len(BaseSettings.__fields__)
    assert re.search(r"debug\s+False", text)
    assert re.search(r"api_token_payload\s+\*+", text)  # masked secret


def test_settings_env() -> None:
    # Test settings can be converted to a dict of environment variables
    settings = BaseSettings.get()
    env = settings.env()

    assert env["MEX_DEBUG"] == "false"
    assert env["MEX_PUBLIC_API_TOKEN_PAYLOAD"].startswith("cGF5bG9hZA")  # plain secret


def test_settings_env_text() -> None:
    # Test settings can be converted to multi-line .env-file text
    settings = BaseSettings.get()
    env = settings.env_text()

    assert len(env.splitlines()) == len(settings.env())
    assert re.search(r'MEX_DEBUG="false"', env)
    assert re.search(
        r'MEX_PUBLIC_API_TOKEN_PAYLOAD="cGF5bG9hZA=="', env
    )  # plain secret


class FooSettings(BaseSettings):
    """Dummy settings subclass for testing."""

    foo: str = "foo"


def test_stetings_getting_caches_singleton() -> None:
    # clear cache
    SettingsContext.set(None)  # clear cache

    # first get
    settings = FooSettings.get()
    cached_settings = SettingsContext.get()
    assert settings is cached_settings

    # repeated get
    settings_fetched_again = FooSettings.get()
    assert settings_fetched_again is settings


def test_settings_getting_wrong_class_raises_error() -> None:
    # initial type is determined by `settings` fixture
    assert isinstance(SettingsContext.get(), BaseSettings)

    with pytest.raises(RuntimeError, match="already loaded"):
        FooSettings.get()
