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
- **[gitleaks](https://github.com/gitleaks/gitleaks)**, pinned in
  [CONTRIBUTING.md](CONTRIBUTING.md#getting-set-up).
- No external services. Configuration is optional — see Usage below.

## Installation

See [`docs/INSTALL.md`](docs/INSTALL.md) for every install method — the
AUR, Nix, `.deb`/`.rpm` release assets, and installing from a checkout.
For development, or to run from a checkout:

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

`api_token` is the example credential field, and it takes a second form
too: `api_token_command` (`--api-token-command` /
`SCAFFOLD_PYTHON_CLI_API_TOKEN_COMMAND`) runs a command through the shell
and uses its trimmed stdout as the token instead — the same shape as
restic's `--password-command`, msmtp's `passwordeval`, Borg's
`BORG_PASSCOMMAND`. If both `api_token` and `api_token_command` are set,
the command wins, and a command that exits non-zero fails the run rather
than silently resolving to an empty token. `init` never writes a literal
value for `api_token` — the config file it generates shows the `_command`
form commented out as an example, pointing at
`hush-hush get <object-key>` (swap in whatever this account's own secrets
tooling is):

```toml
# api_token_command = "hush-hush get scaffold-python-cli-api-token"
```

## Reports

Every push to `main` publishes the test and coverage reports to GitHub Pages:

- Coverage: <https://apis.ryankes.eu/scaffold-python-cli/reports/coverage/>,
  with the Cobertura file at `.../reports/coverage/coverage.xml`.
- Test results: <https://apis.ryankes.eu/scaffold-python-cli/reports/tests/>,
  with the JUnit XML at `.../reports/tests/junit.xml`.

A repo generated from this template publishes under its own name, with no edit
needed: turn on Pages (source: GitHub Actions) and the next push to `main`
deploys. Pull requests assemble the reports but don't deploy them. A user-site
repo (`<owner>.github.io`) is served at `/reports/` with no repo prefix; the
workflow follows the deployed `page_url`, so it needs no change either.
There's no Lighthouse report, since a command-line tool has no web page to audit.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the toolchain, the hooks, and
how a change gets reviewed and released.

## Actions event policy

The workflows here use `pull_request_target`, which GitHub's default Actions
policy blocks on public repos from 2026-12-02. A new public repo made from this
template needs a per-repo policy allowing the events its workflows use, or
those workflows end in `startup_failure`:

```sh
gh api -X POST repos/<owner>/<repo>/actions/policies --input - <<'JSON'
{"name":"allow-pull_request_target","enforcement":"active",
 "rules":[{"type":"restrict_action_events",
           "parameters":{"allowed_events":["pull_request_target","pull_request","push"]}}]}
JSON
```

`allowed_events` is an allow-list: add every other event a workflow uses
(`schedule`, `workflow_dispatch`, `workflow_run`, `release` and so on), or it
stops firing. A later change to an existing policy is made in the UI under
Settings > Actions > Policies. See the
[GitHub docs](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target).

## Licence

No licence has been chosen yet — see [`LICENSE`](LICENSE). Pick one before
a project stamped from this template goes anywhere public.
