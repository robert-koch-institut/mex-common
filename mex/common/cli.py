import json
import pdb  # noqa: T100
import sys
from bdb import BdbQuit
from collections.abc import Callable
from functools import partial
from textwrap import dedent
from traceback import format_exc
from typing import Any

import click
from click import Command, Option
from click.core import ParameterSource
from click.exceptions import Abort, Exit
from pydantic.fields import FieldInfo

from mex.common.connector import CONNECTOR_STORE
from mex.common.logging import logger
from mex.common.settings import SETTINGS_STORE, BaseSettings
from mex.common.transform import MExEncoder

HELP_TEMPLATE = """
{doc}

Acceptable configuration sources sorted by priority:
(1) command line arguments and options
(2) environment variables
(3) dotenv file located at {env_file}
(4) default values from settings model
"""


def _field_to_parameters(name: str, field: FieldInfo) -> list[str]:
    """Convert a field of a pydantic settings class into parameter declarations.

    The field's name and alias are considered. Underscores are replaced with dashes
    and single character parameters have two leading dashes while single character
    parameters have just one.

    Args:
        name: name of the Field
        field: Field of a Settings definition class

    Returns:
        List of parameter declaring strings
    """
    names = [name] + ([field.alias] if field.alias else [])
    names = [n.replace("_", "-") for n in names]
    dashes = ["--" if len(n) > 1 else "-" for n in names]
    return [f"{d}{n}" for d, n in zip(dashes, names, strict=False)]


def _field_to_option(name: str, settings_cls: type[BaseSettings]) -> Option:
    """Convert a field of a pydantic settings class into a click option.

    Args:
        name: name of the Field
        settings_cls: Base settings class or a subclass of it

    Returns:
        Option: click Option with appropriate attributes
    """
    # normalize field type to be compatible with advanced string types
    # https://pydantic-docs.helpmanual.io/usage/types/#pydantic-types
    # complex fields or type unions are always interpreted as strings
    # and add support for SecretStr fields with correct default values
    # https://pydantic-docs.helpmanual.io/usage/types/#secret-types
    field = settings_cls.model_fields[name]

    if field.annotation in (int, bool, float):
        field_type: Any = field.annotation
    else:
        field_type = str

    if field.is_required():
        default = None
    elif field.annotation in (int, bool, float):
        default = field.default
    else:
        default = json.dumps(field.default, cls=MExEncoder).strip('"')

    return Option(
        _field_to_parameters(name, field),
        default=default,
        envvar=settings_cls.get_env_name(name),
        help=field.description,
        is_flag=field.annotation is bool and field.default is False,
        show_default=True,
        show_envvar=True,
        type=field_type,
        required=field.is_required(),
    )


def _callback(
    func: Callable[[], None],
    settings_cls: type[BaseSettings],
    **cli_settings: str,
) -> None:
    """Run the decorated function in the current click context.

    When `cli_settings` specify debug mode and an exception occurs,
    jump into post mortem debugging and raise exception.

    Args:
        func: Entry point function for a cli
        settings_cls: Base settings class or a subclass of it
        cli_settings: Parsed settings in string format

    Raises:
        Exception: Any uncaught exception when in debug mode
        SysExit: With exit code 0 or 1
    """
    # get current click context.
    context = click.get_current_context()

    # ensure all singletons are reset.
    context.call_on_close(CONNECTOR_STORE.reset)
    context.call_on_close(SETTINGS_STORE.reset)

    # load settings from parameters and store it globally.
    settings = settings_cls.model_validate(
        {
            key: value
            for key, value in cli_settings.items()
            if context.get_parameter_source(key) == ParameterSource.COMMANDLINE
        }
    )
    SETTINGS_STORE.push(settings)

    # otherwise print loaded settings in pretty way and continue.
    logger.info(click.style(dedent(f"    {func.__doc__}"), fg="green"))
    logger.info(click.style(f"{settings.text()}\n", fg="bright_cyan"))

    # now try to execute the decorated function.
    try:
        func()
    except (Abort, BdbQuit, Exit, KeyboardInterrupt):  # pragma: no cover
        context.exit(130)
    except Exception:
        # an error occurred, let's print the traceback
        logger.error(click.style(format_exc(), fg="red"))
        if settings.debug:  # pragma: no cover
            # if we are in debug mode, jump into interactive debugging.
            pdb.post_mortem(sys.exc_info()[2])
            raise
        # if not in debug mode, exit with code 1.
        logger.error("exit")
        context.exit(1)

    # all good, exit with code 0.
    logger.info("done")
    context.exit(0)


def entrypoint(
    settings_cls: type[BaseSettings],
) -> Callable[[Callable[[], None]], Command]:
    """Decorate given function to mark it as a cli entrypoint.

    The decorator takes one argument `settings_cls` that is either
    `mex.common.settings.BaseSettings` or a subclass thereof. The decorated function
    must not require any positional arguments and does not need to return anything.

    Running an `entrypoint` will print a summary on startup, register settings and
    connector singletons globally and provide error handling as well as debugging.

    Args:
        settings_cls: Settings class that should be instantiated globally.

    Returns:
        Callable: The decorated function with initialized settings.
    """

    def decorator(func: Callable[[], None]) -> Command:
        return Command(
            func.__name__,
            help=HELP_TEMPLATE.format(
                doc=func.__doc__, env_file=settings_cls.model_config.get("env_file")
            ),
            callback=partial(_callback, func, settings_cls),
            params=[
                _field_to_option(name, settings_cls)
                for name in settings_cls.model_fields
            ],
        )

    return decorator
