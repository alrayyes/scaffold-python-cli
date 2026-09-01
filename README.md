# scaffold-python-cli

[![CI](https://github.com/alrayyes/scaffold-python-cli/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/alrayyes/scaffold-python-cli/actions/workflows/ci.yml)
[![Codecov](https://codecov.io/gh/alrayyes/scaffold-python-cli/graph/badge.svg)](https://codecov.io/gh/alrayyes/scaffold-python-cli)
[![release](https://img.shields.io/github/v/release/alrayyes/scaffold-python-cli?sort=semver)](https://github.com/alrayyes/scaffold-python-cli/releases/latest)
[![licence](https://img.shields.io/badge/licence-unlicensed-lightgrey)](LICENSE)

A GitHub template for a Python command-line tool. Run `gh repo create
my-real-project --template alrayyes/scaffold-python-cli` and you get a
project with the conventions already wired in — pinned tooling, a
[Typer](https://typer.tiangolo.com) command, prose linting, secret
scanning, and release automation — rather than a blank directory and a
checklist to work through by hand.

It isn't a product on its own. The one command it ships, `greet`, exists
so the whole chain — code, tests, hooks, CI — has something real to run
against. Replace it with your first real command and delete this
paragraph.

The tooling this template wires in is GitHub-primary. If a project stamped
from it ends up hosted on Forgejo instead, see
[FORGEJO.md](FORGEJO.md) for what to swap in.

## Requirements

- **Python 3.13 or newer.**
- **[uv](https://docs.astral.sh/uv/)**, for the virtual environment, the
  dependencies and running everything below. Not installed by default —
  one-time setup:

  ```sh
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  Confirm it worked with `uv --version`.

- **[bun](https://bun.sh)**, for the tooling that isn't Python —
  commitlint, Prettier, markdownlint, and the
  [lefthook](https://lefthook.dev) that runs the git hooks. There's a
  `package.json`, but nothing here is JavaScript; it exists only so those
  tools resolve and stay pinned.
- **[Vale](https://vale.sh)**, pinned in
  [CONTRIBUTING.md](CONTRIBUTING.md#getting-set-up).
- No external services. Configuration is optional — see Usage below.

## Installation

```sh
git clone https://github.com/alrayyes/scaffold-python-cli.git
cd scaffold-python-cli
uv sync
```

## Usage

```sh
uv run scaffold-python-cli greet --name World
```

Prints `Hello, World!`.

A run with no config file yet offers to create one — answer no, or run
non-interactively (CI, a script, a pipe), and it just runs on defaults.
`init` writes the starter file directly:

```sh
uv run scaffold-python-cli init
```

Every setting takes a flag, an environment variable
(`SCAFFOLD_PYTHON_CLI_<SETTING>`), or a line in the config file
(`$XDG_CONFIG_HOME/scaffold-python-cli/config.toml`, usually
`~/.config/scaffold-python-cli/config.toml`) — in that order of
precedence. `--verbose` / `SCAFFOLD_PYTHON_CLI_VERBOSE` / `verbose = true`
all do the same thing; `--no-verbose` overrides either of the other two
back off.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the toolchain, the hooks, and
how a change gets reviewed and released.

## Licence

No licence has been chosen yet — see [`LICENSE`](LICENSE). Pick one before
a project stamped from this template goes anywhere public.
