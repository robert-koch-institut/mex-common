import json
import pdb
import sys
from bdb import BdbQuit
from enum import Enum
from functools import partial
from textwrap import dedent
from traceback import format_exc
from typing import Callable, Union, get_origin

import click
from click import Command, Option
from click.core import ParameterSource
from click.exceptions import Abort, Exit
from pydantic import SecretStr
from pydantic.fields import ModelField

from mex.common.connector import reset_connector_context
from mex.common.logging import echo
from mex.common.settings import SettingsContext, SettingsType
from mex.common.transform import MExEncoder

HELP_TEMPLATE = """
{doc}

Acceptable configuration sources sorted by priority:
(1) command line arguments and options
(2) environment variables
(3) dotenv file located at {env_file}
(4) default values from settings model
"""


def field_to_parameters(field: ModelField) -> list[str]:
    """Convert a field of a pydantic settings class into parameter declarations.

    The field's name and alias are considered. Underscores are replaced with dashes
    and single character parameters have two leading dashes while single character
    parameters have just one.

    Args:
        field: Field of a Settings definition class

    Returns:
        List of parameter declaring strings
    """
    names = [n.replace("_", "-") for n in sorted({field.name, field.alias}) if n]
    dashes = ["--" if len(n) > 1 else "-" for n in names]
    return [f"{d}{n}" for d, n in zip(dashes, names)]


def field_to_option(field: ModelField) -> Option:
    """Convert a field of a pydantic settings class into a click option.

    Args:
        field: Field of a Settings definition class

    Returns:
        Option: click Option with appropriate attributes
    """
    # normalize field type to be compatible with advanced string types
    # https://pydantic-docs.helpmanual.io/usage/types/#pydantic-types
    # complex fields or type unions are always interpreted as strings
    # and add support for SecretStr fields with correct default values
    # https://pydantic-docs.helpmanual.io/usage/types/#secret-types
    if (
        field.is_complex()
        or get_origin(field.type_) is Union
        or issubclass(field.type_, (str, SecretStr, Enum))
    ):
        field_type = str
        default = json.dumps(field.default, cls=MExEncoder).strip('"')
    else:
        field_type = field.type_
        default = field.default
    return Option(
        field_to_parameters(field),
        default=default,
        envvar=list(field.field_info.extra["env_names"])[0].upper(),
        help=field.field_info.description,
        is_flag=field.type_ is bool and field.default is False,
        show_default=True,
        show_envvar=True,
        type=field_type,
    )


def callback(
    func: Callable[[], None],
    settings_cls: type[SettingsType],
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

    # ensure connectors are closed on exit.
    context.call_on_close(reset_connector_context)

    # load settings from parameters and store in ContextVar.
    settings = settings_cls.parse_obj(
        {
            key: value
            for key, value in cli_settings.items()
            if context.get_parameter_source(key) == ParameterSource.COMMANDLINE
        }
    )
    SettingsContext.set(settings)

    # print .env-style settings if echo-settings flag is set, then exit.
    if cli_settings.get("echo_settings"):
        click.secho(settings.env_text())
        context.exit(0)

    # otherwise print loaded settings in pretty way and continue
    click.secho(dedent(f"    {func.__doc__}"), fg="green")
    click.secho(f"{settings.text()}\n", fg="bright_cyan")

    # now try to exectute the decorated function.
    try:
        func()
    except (Abort, BdbQuit, Exit, KeyboardInterrupt):  # pragma: no cover
        context.exit(130)
    except Exception as error:
        # an error occured, let's print the traceback
        click.secho(format_exc(), fg="red")
        if settings.debug:  # pragma: no cover
            # if we are in debug mode, jump into interactive debugging.
            pdb.post_mortem(sys.exc_info()[2])
            raise error
        # if not in debug mode, exit with code 1
        echo("exit", fg="red")
        context.exit(1)

    # all good, exit with code 0.
    echo("done", fg="green")
    context.exit(0)


def entrypoint(
    settings_cls: type[SettingsType],
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
        meta_parameters = [
            Option(
                ["--echo-settings"],
                help="Echo current settings in .env format and exit.",
                is_flag=True,
                type=bool,
            )
        ]
        return Command(
            func.__name__,
            help=HELP_TEMPLATE.format(
                doc=func.__doc__, env_file=settings_cls.__config__.env_file
            ),
            callback=partial(callback, func, settings_cls),
            params=[
                *[field_to_option(field) for field in settings_cls.__fields__.values()],
                *meta_parameters,
            ],
        )

    return decorator
