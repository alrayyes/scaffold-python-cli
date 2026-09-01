"""A run with no config file and no relevant environment variable set
offers to run `init` right there, rather than silently falling back to
bare defaults or erroring with no path forward -- a genuinely
unconfigured first run is exactly the moment someone needs pointing at
`init`, not left to find it in --help. Once a config file exists, stop
asking; this is a first-run prompt, not a nag on every invocation.

Checks for a TTY before prompting, and fails closed without one -- CI and
any piped or scripted invocation has no TTY, and a prompt that blocks on
input a script will never send hangs the job instead of failing it fast.
"""

from __future__ import annotations

import os
from typing import IO

from scaffold_python_cli.config import VERBOSE_ENV_VAR, config_file_path, write_starter_config


def maybe_offer_init(
    *,
    stdin: IO[str],
    stdout: IO[str],
    stderr: IO[str],
    is_terminal: bool,
    skip_prompt: bool,
) -> None:
    path = config_file_path()

    if path.exists():
        return  # this is a first-run prompt, not a nag on every invocation.

    if VERBOSE_ENV_VAR in os.environ:
        return

    if skip_prompt:
        written = write_starter_config(force=False, path=path)
        stdout.write(f"Wrote {written}\n")
        return

    if not is_terminal:
        stderr.write(
            f"no config file found at {path}; run `scaffold-python-cli init` to create one, "
            "or pass --yes to create it now. Continuing with defaults.\n"
        )
        return

    stdout.write(f"No config file found at {path}.\nRun `init` now? [y/N] ")
    stdout.flush()
    answer = stdin.readline()

    if answer.strip().lower() == "y":
        written = write_starter_config(force=False, path=path)
        stdout.write(f"Wrote {written}\n")
