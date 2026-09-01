"""The Typer app. One example command, `greet`, so the whole chain — CLI,
tests, hooks, CI — has something real to run against. Replace it with your
first real command and delete this comment.

It also reads the config file this template ships (config.py), so the
flags-over-env-over-file-over-defaults precedence has something real to
observe: pass --verbose, set SCAFFOLD_PYTHON_CLI_VERBOSE, or write
`verbose = true` to the config file and the extra detail below shows up
the same way regardless of which layer set it.

--api-token/--api-token-command demonstrate the same layering for a
credential field, plus the command-form resolution cli.md requires:
`greet --verbose` only reports whether a token resolved, since this
template has no real service to send it to.
"""

import platform
import sys

import typer

from scaffold_python_cli.config import (
    Config,
    SecretCommandError,
    load_file_config,
    resolve_secret,
    write_starter_config,
)
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
    api_token: str = typer.Option(
        "",
        "--api-token",
        help="Credential example, literal form -- prefer --api-token-command instead.",
    ),
    api_token_command: str = typer.Option(
        "",
        "--api-token-command",
        help="Command whose trimmed stdout supplies the token; wins over "
        "--api-token when both are set.",
    ),
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

    # click already resolved --verbose/--api-token/--api-token-command
    # against the flag and the env var above; "DEFAULT" means neither
    # supplied one, so this is the only place the file layer gets a
    # chance to apply. Compared by name, not by importing
    # click.core.ParameterSource directly: Typer vendors its own copy of
    # click (typer._click), and get_parameter_source() returns a member
    # of *that* enum, not the standalone click package's -- an `is`/`==`
    # against the wrong one silently never matches.
    source = ctx.get_parameter_source("verbose")
    if source is not None and source.name == "DEFAULT":
        verbose = load_file_config().verbose

    source = ctx.get_parameter_source("api_token")
    if source is not None and source.name == "DEFAULT":
        api_token = load_file_config().api_token

    source = ctx.get_parameter_source("api_token_command")
    if source is not None and source.name == "DEFAULT":
        api_token_command = load_file_config().api_token_command

    # Resolved eagerly, on every invocation -- not lazily the first time
    # something needs the token -- so a broken _command fails the run
    # loudly right away rather than wherever it's first read. Per
    # cli.md: never fall back to an empty credential silently.
    try:
        resolved_api_token = resolve_secret(api_token, api_token_command)
    except SecretCommandError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    ctx.obj = Config(
        verbose=verbose, api_token=resolved_api_token, api_token_command=api_token_command
    )


@app.command()
def greet(
    ctx: typer.Context,
    name: str = typer.Option("World", "--name", help="Who to greet."),
) -> None:
    """Print a greeting."""
    cfg: Config = ctx.obj
    if cfg.verbose:
        # Reports presence, never the value -- this template has no
        # service to send a real token to, and echoing a secret back is
        # exactly the habit a config-secrets example shouldn't model.
        auth_note = " (authenticated)" if cfg.api_token else ""
        typer.echo(
            f"Hello, {name}!{auth_note} (python {platform.python_version()}, "
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
