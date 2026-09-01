"""Every setting this tool resolves from flags, the environment and the
config file, in that order -- flags override environment variables
override the config file override built-in defaults, per cli.md.

click's ``auto_envvar_prefix`` (wired in cli.py) handles the flag and
environment layers together; this module is the file layer plus the
dataclass the two combine into.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

import platformdirs
import tomli_w

APP_NAME = "scaffold-python-cli"
ENV_PREFIX = "SCAFFOLD_PYTHON_CLI"
VERBOSE_ENV_VAR = f"{ENV_PREFIX}_VERBOSE"


@dataclass
class Config:
    verbose: bool = False


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
    that. Nothing here can currently be invalid, but every config-backed
    command calls read_config_file/dump_toml through this so a future
    field doesn't skip the check.
    """
    if "verbose" in data and not isinstance(data["verbose"], bool):
        raise ValueError(f"verbose must be a boolean, got {data['verbose']!r}")


def load_file_config(path: Path | None = None) -> Config:
    data = read_config_file(path)
    _validate(data)
    return Config(verbose=bool(data.get("verbose", False)))
