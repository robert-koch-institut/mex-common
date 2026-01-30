import sys
import warnings
from bdb import BdbQuit
from collections.abc import Callable
from functools import partial
from traceback import format_exc

import click
from click import Command, Option
from click.exceptions import Abort, Exit

from mex.common.connector import CONNECTOR_STORE
from mex.common.logging import logger
from mex.common.settings import SETTINGS_STORE, BaseSettings


def _callback(
    func: Callable[[], None],
    settings_cls: type[BaseSettings] | None,
    **cli_settings: object,
) -> None:
    """Run the decorated function in the current click context.

    Args:
        func: Entry point function for a cli
        settings_cls: Base settings class or a subclass of it
        cli_settings: Parsed cli options in raw format

    Raises:
        Exception: Any uncaught exception
        SysExit: With exit code 0 or 1
    """
    # get current click context.
    context = click.get_current_context()

    # get pdb flag from cli_settings
    pdb_post_mortem = cli_settings.get("pdb", False)

    # ensure all singletons are reset.
    context.call_on_close(CONNECTOR_STORE.reset)
    context.call_on_close(SETTINGS_STORE.reset)

    # otherwise print loaded settings in pretty way and continue.
    if func.__doc__:
        logger.info(click.style(func.__doc__.strip(), fg="green"))

    # pre-loading settings is deprecated, they should be instantiated lazily instead
    if settings_cls:
        warnings.warn(
            "The `settings_cls` argument to the `entrypoint` decorator is deprecated, "
            "please remove it. "
            "The settings will be lazy-loaded instead, so no further change is needed.",
            stacklevel=1,
        )
        settings_cls.get()

    # now try to execute the decorated function.
    try:
        func()
    except (Abort, BdbQuit, Exit, KeyboardInterrupt):  # pragma: no cover
        context.exit(130)
    except Exception:
        # an error occurred, let's print the traceback
        logger.error(click.style(format_exc(), fg="red"))
        if pdb_post_mortem:  # pragma: no cover
            # if we are in pdb mode, jump into interactive post-mortem debugger.
            try:
                import ipdb as pdb  # type: ignore[import-untyped] # noqa: PLC0415, T100
            except ImportError:
                import pdb  # noqa: PLC0415, T100
            pdb.post_mortem(sys.exc_info()[2])
            raise
        # if not in pdb mode, exit with code 1.
        logger.error("exit")
        context.exit(1)

    # all good, exit with code 0.
    logger.info("done")
    context.exit(0)


def entrypoint(
    settings_cls: type[BaseSettings] | None = None,
) -> Callable[[Callable[[], None]], Command]:
    """Decorate given function to mark it as a cli entrypoint.

    Running an `entrypoint` will print a summary on startup, provide error handling,
    close connectors on shutdown and adds `--pdb` post mortem debugging.

    Args:
        settings_cls: Settings class (deprecated).

    Returns:
        Callable: The decorated function
    """

    def decorator(func: Callable[[], None]) -> Command:
        return Command(
            func.__name__,
            help=func.__doc__,
            callback=partial(_callback, func, settings_cls=settings_cls),
            params=[
                Option(
                    ("--pdb",),
                    is_flag=True,
                    help="Jump into post-mortem debugging after uncaught exceptions.",
                )
            ],
        )

    return decorator
