"""The Typer app. One example command, `greet`, so the whole chain — CLI,
tests, hooks, CI — has something real to run against. Replace it with your
first real command and delete this comment.

It also reads the config file this template ships (config.py), so the
flags-over-env-over-file-over-defaults precedence has something real to
observe: pass --verbose, set SCAFFOLD_PYTHON_CLI_VERBOSE, or write
`verbose = true` to the config file and the extra detail below shows up
the same way regardless of which layer set it.
"""

import platform
import sys

import typer

from scaffold_python_cli.config import Config, load_file_config, write_starter_config
from scaffold_python_cli.first_run import maybe_offer_init

# click's own auto_envvar_prefix does the environment layer for every
# option below with no per-option envvar= needed -- --verbose becomes
# SCAFFOLD_PYTHON_CLI_VERBOSE.
app = typer.Typer(
    help="scaffold-python-cli: a Typer command-line tool.",
    context_settings={"auto_envvar_prefix": "SCAFFOLD_PYTHON_CLI"},
)


@app.callback()
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose/--no-verbose", help="Enable verbose output."),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Answer yes to the first-run config prompt without asking.",
    ),
) -> None:
    """scaffold-python-cli: a Typer command-line tool."""
    # init has its own reason for existing; asking it to run itself first
    # would be silly, so every other command runs through this first-run
    # check instead.
    if ctx.invoked_subcommand != "init":
        maybe_offer_init(
            stdin=sys.stdin,
            stdout=sys.stdout,
            stderr=sys.stderr,
            is_terminal=sys.stdin.isatty(),
            skip_prompt=yes,
        )

    # click already resolved --verbose against the flag and the env var
    # above; "DEFAULT" means neither supplied one, so this is the only
    # place the file layer gets a chance to apply. Compared by name, not
    # by importing click.core.ParameterSource directly: Typer vendors its
    # own copy of click (typer._click), and get_parameter_source() returns
    # a member of *that* enum, not the standalone click package's -- an
    # `is`/`==` against the wrong one silently never matches.
    source = ctx.get_parameter_source("verbose")
    if source is not None and source.name == "DEFAULT":
        verbose = load_file_config().verbose

    ctx.obj = Config(verbose=verbose)


@app.command()
def greet(
    ctx: typer.Context,
    name: str = typer.Option("World", "--name", help="Who to greet."),
) -> None:
    """Print a greeting."""
    cfg: Config = ctx.obj
    if cfg.verbose:
        typer.echo(
            f"Hello, {name}! (python {platform.python_version()}, "
            f"{platform.system()}/{platform.machine()})"
        )
    else:
        typer.echo(f"Hello, {name}!")


@app.command()
def init(
    force: bool = typer.Option(False, "--force", help="Overwrite an existing config file."),
) -> None:
    """Write a starter config file."""
    path = write_starter_config(force=force)
    typer.echo(f"Wrote {path}")


def main() -> None:
    app()
