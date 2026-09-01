# scaffold-python-cli

A GitHub template repo, not a running tool. It's built from
`~/.config/claude/CLAUDE.md` and `~/.config/claude/rules/*.md` — read those
for the "why" behind everything below. This file only says what's specific
to this repo.

## What this is

Bootstrapped in the PR sequence documented in
`~/.config/claude/plans/adaptive-conjuring-karp.md`: chassis, prose tooling,
docs, code, CI, prose/secret CI, release automation, Dependabot — each in
its own PR. Keep new work in that shape: one concern per PR.

## Commands

```sh
uv run pytest
uv run ruff check                  # uv run ruff check --fix is the fixer
uv run ruff format --check         # uv run ruff format is the fixer
bun run format:check               # bun run lint:md, lint:prose, lint:mechanics too
```

Full list and what each one does: [CONTRIBUTING.md](CONTRIBUTING.md).

## Gotchas

- **Branch protection is on.** This repo is public, so the paid-plan
  restriction that blocks it on a private repo doesn't apply here — `main`
  requires a pull request, set up the same way as any other
  `github.com/alrayyes` repo.
- **uv, not pip.** The two real local Python repos
  (`org-roam-to-obsidian`, `freelance-archiver`) both use
  `requirements-dev.txt`; this template deliberately diverges to `uv` +
  `pyproject.toml` + `uv.lock`, per the bootstrap plan's decision. Don't
  "fix" it back to pip on the strength of local precedent.
- **Typer, not `argparse`.** Chosen to mirror cobra's thin-command-layer
  pattern from the Go scaffolds. `tests/test_cli.py` drives it through
  `typer.testing.CliRunner`, not by shelling out to the built package.
- **ruff does both jobs.** `[tool.ruff]` in `pyproject.toml` covers linting
  and formatting — no flake8, no black, no isort. `ruff check` is the
  linter, `ruff format` the formatter; both have a `--check`/non-writing
  mode for CI and a writing mode for the pre-commit hook.
- **Flat `src/` layout, on purpose.** Everything importable lives at
  `src/scaffold_python_cli/`. Don't pre-build a `commands/` subpackage —
  that shape earns its place the day a second command needs its own file.
- **The example command is a placeholder.** `greet` exists so the whole
  chain (code, tests, CI) has something real to run end to end. A project
  stamped from this template replaces it with its first real command.
- **`LICENSE` is deliberately unpicked.** Don't default it to GPL-3.0 or
  anything else; that's a decision the project stamped from this template
  makes, not this template.
- **Renovate can't reach this repo.** It's GitHub-primary; Dependabot
  (`.github/dependabot.yml`) is what raises dependency pull requests here.
- **Packaging (PyInstaller/.deb/.rpm/AUR/Nix) is real, not a stub.**
  `Dockerfile`'s `pyinstaller` stage, `nfpm.yaml`, `PKGBUILD` and
  `flake.nix` all match the reference implementation proved out in
  `alrayyes/movie-planner`, verified end to end (a real PyInstaller
  binary, a real `.deb`/`.rpm` install in a non-slim Debian/Fedora
  container, a real `makepkg` build/install, a real `nix build`/`nix
run`) rather than eyeballed. A project stamped from this template
  renames `scaffold-python-cli` throughout those files (and
  `docs/INSTALL.md`) the same day it replaces `greet`.
