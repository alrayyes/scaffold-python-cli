"""Every setting this tool resolves from flags, the environment and the
config file, in that order -- flags override environment variables
override the config file override built-in defaults, per cli.md.

click's ``auto_envvar_prefix`` (wired in cli.py) handles the flag and
environment layers together; this module is the file layer plus the
dataclass the two combine into.

``api_token``/``api_token_command`` demonstrate cli.md's "Secrets get a
command option, not just a value": a credential field always ships with
a ``_command`` sibling that runs a command and uses its trimmed stdout
instead, so a real project stamped from this template has a working
example to copy rather than a rule to reimplement from prose.
"""

from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

import platformdirs
import tomli_w

APP_NAME = "scaffold-python-cli"
ENV_PREFIX = "SCAFFOLD_PYTHON_CLI"
VERBOSE_ENV_VAR = f"{ENV_PREFIX}_VERBOSE"
API_TOKEN_ENV_VAR = f"{ENV_PREFIX}_API_TOKEN"
API_TOKEN_COMMAND_ENV_VAR = f"{ENV_PREFIX}_API_TOKEN_COMMAND"


class SecretCommandError(RuntimeError):
    """Raised when a `<field>_command` exits non-zero. Per cli.md: fail
    loudly rather than silently falling back to an empty credential.
    """


def resolve_secret(literal: str, command: str) -> str:
    """The credential to actually use: ``command``'s trimmed stdout when
    it's set -- it always wins over a lingering literal value, since
    someone who configured the command form did it on purpose -- the
    literal value otherwise.

    Runs through the shell so `hush-hush get <key>`, `pass show <path>`,
    or a pipeline all work unmodified. Trims exactly one trailing
    newline, not every trailing newline a command happens to print, and
    raises rather than returning "" when the command exits non-zero.
    """
    if not command:
        return literal

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise SecretCommandError(
            f"command {command!r} exited {result.returncode}: {result.stderr.strip()}"
        )

    stdout = result.stdout
    return stdout[:-1] if stdout.endswith("\n") else stdout


@dataclass
class Config:
    verbose: bool = False
    api_token: str = ""
    api_token_command: str = ""

    def resolved_api_token(self) -> str:
        """``api_token`` as it should actually be used -- see
        ``resolve_secret``."""
        return resolve_secret(self.api_token, self.api_token_command)


def config_file_path() -> Path:
    """The config file's path under the XDG config directory --
    $XDG_CONFIG_HOME/scaffold-python-cli/config.toml, falling back to
    ~/.config/scaffold-python-cli/config.toml when the environment
    variable is unset. See cli.md's XDG Base Directory section.
    """
    return Path(platformdirs.user_config_dir(APP_NAME, appauthor=False)) / "config.toml"


def read_config_file(path: Path | None = None) -> dict:
    """Read the config file, if present. A missing file is not an error --
    bare defaults are exactly what an unconfigured run falls back to.
    """
    path = path or config_file_path()
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except FileNotFoundError:
        return {}


STARTER_CONFIG_HEADER = """\
# scaffold-python-cli config file.
# Flags and environment variables (SCAFFOLD_PYTHON_CLI_<SETTING>) override
# whatever's set here -- see `scaffold-python-cli --help`.
#
# api_token holds a credential. Never write a literal value here -- point
# the _command sibling at wherever this account keeps it instead, e.g.:
# api_token_command = "hush-hush get scaffold-python-cli-api-token"

"""

DEFAULT_CONFIG: dict = {"verbose": False}


def write_starter_config(force: bool = False, path: Path | None = None) -> Path:
    """Write the starter config -- the defaults a run would otherwise
    fall back to silently, rendered by tomli-w (tomllib is read-only) and
    ready to edit -- refusing to overwrite an existing file unless force
    is set.
    """
    path = path or config_file_path()
    if not force and path.exists():
        raise FileExistsError(f"{path} already exists; pass --force to overwrite")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(STARTER_CONFIG_HEADER + tomli_w.dumps(DEFAULT_CONFIG), encoding="utf-8")
    path.chmod(0o600)
    return path


def _validate(data: dict) -> None:
    """Catches a bad value at startup rather than wherever it's first
    read -- config from a file on disk can't be trusted further than
    that. Every config-backed command calls read_config_file/dump_toml
    through this so a future field doesn't skip the check.
    """
    if "verbose" in data and not isinstance(data["verbose"], bool):
        raise ValueError(f"verbose must be a boolean, got {data['verbose']!r}")
    for field in ("api_token", "api_token_command"):
        if field in data and not isinstance(data[field], str):
            raise ValueError(f"{field} must be a string, got {data[field]!r}")


def load_file_config(path: Path | None = None) -> Config:
    data = read_config_file(path)
    _validate(data)
    return Config(
        verbose=bool(data.get("verbose", False)),
        api_token=str(data.get("api_token", "")),
        api_token_command=str(data.get("api_token_command", "")),
    )
