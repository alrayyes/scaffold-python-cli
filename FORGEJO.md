# Running this on Forgejo instead of GitHub

This template defaults to GitHub-primary tooling: release-please cuts
releases from `.github/workflows/release.yml`, Dependabot raises dependency
pull requests from `.github/dependabot.yml`, and everything else runs out of
`.github/workflows/`. None of that follows a project onto a self-hosted
Forgejo instance — three things are GitHub-specific and need swapping, not
adapting. This is what to put in their place, with working examples rather
than a description of the shape.

The examples below are adapted from two real, currently running setups: a
Hugo site publishing releases to Forgejo with semantic-release (including
its `.forgejo/workflows/ci.yml`), and a Renovate bot with `autodiscover`
running across a Forgejo instance's other repositories. Where this
scaffold's own Python toolchain needed something neither of those examples
covers — bumping a version that lives in `pyproject.toml` rather than
`package.json` — that part is a reasoned adaptation of the same pattern,
flagged as such below, not a copy-paste from a project already running it.
Domains, tokens and repository paths below are placeholders; swap in
whatever the target Forgejo instance actually is.

## 1) Release automation: release-please → semantic-release

`release-please-config.json` and `.github/workflows/release.yml` only work as
a GitHub Action — `googleapis/release-please-action` is published to the
GitHub Marketplace and reads GitHub's pull-request API to keep its release
pull request up to date. Per this house's own rule (`rules/releases.md`):
release-please is GitHub-only, so anything hosted on Forgejo wants
semantic-release instead.

Swap in [semantic-release](https://semantic-release.gitbook.io/) plus
[`@ribbon-studios/semantic-release-forgejo`](https://www.npmjs.com/package/@ribbon-studios/semantic-release-forgejo),
the plugin that publishes the release itself to a Forgejo instance in place
of GitHub or GitLab. A production Hugo site in this house runs exactly this
combination; the config below is that repo's `release.config.mjs`, adapted
to this scaffold's branch name and version file, with the real instance's
domain and repository path replaced by placeholders.

### Tags: check `include-v-in-tag` before you copy anyone else's `tagFormat`

`release-please-config.json` in this repo already sets
`"include-v-in-tag": true`, so any tags it has cut are `v0.1.0`-shaped.
semantic-release's default `tagFormat` is also `v${version}` — so, unlike
a repo that releases bare tags like `17.1.184` and has to override
`tagFormat` to stop semantic-release concluding the repo has never released
and re-publishing `1.0.0` over years of history (a real trap the house's own
Hugo site hit and now guards with a test), **a project stamped from
this template needs no `tagFormat` override**, as long as it releases through
release-please at least once before switching. If it never has — no tags
exist yet — the default also does the right thing. Only override it if you
deliberately want bare tags instead.

### The Python-specific nuance: there is no `@semantic-release/npm` for `pyproject.toml`

Two things are worth establishing before wiring this up, because the answer
here is not the Go/TypeScript answer:

- **This command-line tool does not currently expose its version at runtime.**
  `src/scaffold_python_cli/cli.py` has no `--version` flag and no
  `importlib.metadata.version()` call. The only place a version number lives
  today is `[project].version` in `pyproject.toml` — the same field
  release-please's `"release-type": "python"` already bumps. Releasing
  therefore means exactly what it means today: a bumped `pyproject.toml`, an
  updated `CHANGELOG.md`, a tag, and a Forgejo release — nothing about
  runtime version exposure changes by switching release tools.
- **If a `--version` flag gets added later**, wire it through
  `importlib.metadata.version("scaffold-python-cli")` rather than a literal
  string duplicated in `cli.py`. `importlib.metadata` reads whatever was in
  `pyproject.toml` at build/install time, off the installed package's own
  metadata — the same way Go would read a `ldflags -X main.version=`, except
  here there is nothing to inject at build time at all. As long as
  `pyproject.toml` is bumped _before_ `uv build` runs, `--version` stays
  correct with no further wiring.

Unlike `@semantic-release/npm`, which bumps `package.json` via `npm version`
as a side effect of (never) publishing to a registry, there is no
semantic-release plugin that bumps a `[project].version` field in
`pyproject.toml` out of the box. `@semantic-release/exec` running a small,
purpose-built script is the same shape that Hugo site's own release config
already uses to avoid pulling npm onto a bun runner for the same reason —
bumping a manifest field that its own package manager's release plugin
doesn't apply to. Adapting its `scripts/set-version.sh` (which rewrites
`package.json`) to rewrite `pyproject.toml` instead:

```sh
#!/usr/bin/env bash
# scripts/set-version.sh — rewrites [project].version in pyproject.toml.
# Called by semantic-release's prepareCmd; there is rarely a reason to run
# it by hand. Anchored on a line rewrite rather than a TOML parse-and-
# reserialise, same reasoning as the package.json version of this script:
# nothing here should be able to reorder keys or reformat the file just
# because it also bumped a version, and ruff/prettier check this file's
# formatting on every push.
set -euo pipefail

version=$1
manifest=${PYPROJECT_TOML:-pyproject.toml}

if ! printf '%s' "$version" | grep -qE '^[0-9A-Za-z.+-]+$'; then
  echo "set-version.sh: refusing to write '${version}': not a version" >&2
  exit 1
fi

matches=$(grep -cE '^version = "[^"]*"$' "$manifest")
if [ "$matches" -ne 1 ]; then
  echo "set-version.sh: ${manifest} has ${matches} version fields, expected 1" >&2
  exit 1
fi

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
sed -E "s|^version = \"[^\"]*\"\$|version = \"${version}\"|" "$manifest" >"$tmp"
cat "$tmp" >"$manifest"
```

And `release.config.mjs` at the repo root, adapted from that Hugo site's
config (same Forgejo plugin, same token-handling reasoning —
`forgejoToken` as a plugin option beats the runner's own automatic
`FORGEJO_TOKEN`, which has repository write and would otherwise authenticate
the release silently and wrongly):

```js
// semantic-release's config. JavaScript, not .releaserc.json, because the
// Forgejo plugin's token cannot be passed any other way — see below.
const forgejoUrl =
  process.env.FORGEJO_SERVER_URL ?? "https://forgejo.example.com";

export default {
  branches: ["main"],
  // No tagFormat override: release-please-config.json already sets
  // include-v-in-tag: true, so existing tags are v-prefixed and match
  // semantic-release's own default (v${version}).
  plugins: [
    ["@semantic-release/commit-analyzer", { preset: "conventionalcommits" }],
    [
      "@semantic-release/release-notes-generator",
      { preset: "conventionalcommits" },
    ],
    ["@semantic-release/changelog", { changelogTitle: "# Changelog" }],
    // No @semantic-release/npm — this isn't a JavaScript package, and even
    // if it were, npm has nothing to do with pyproject.toml. exec calls the
    // adapted set-version.sh instead.
    [
      "@semantic-release/exec",
      { prepareCmd: "./scripts/set-version.sh ${nextRelease.version}" },
    ],
    [
      "@ribbon-studios/semantic-release-forgejo",
      { forgejoUrl, forgejoToken: process.env.RELEASE_TOKEN },
    ],
    [
      "@semantic-release/git",
      {
        assets: ["CHANGELOG.md", "pyproject.toml"],
        message: "chore(release): ${nextRelease.version} [skip ci]",
      },
    ],
  ],
};
```

Pin the same plugin versions that Hugo site runs (its `package.json`
devDependencies, exact and locked in `bun.lock`):

```json
"@ribbon-studios/semantic-release-forgejo": "0.1.3",
"@semantic-release/changelog": "7.0.0",
"@semantic-release/commit-analyzer": "13.0.1",
"@semantic-release/exec": "7.1.0",
"@semantic-release/git": "11.0.1",
"@semantic-release/release-notes-generator": "14.1.1",
"conventional-changelog-conventionalcommits": "10.2.1",
"semantic-release": "25.0.9"
```

### `.forgejo/workflows/release.yml`

The one place a real Node matters. This scaffold's own `package.json`
carries bun-tooling only so commitlint/Prettier/markdownlint resolve — the
release job is the exception, because bun 1.3 reports itself as Node
`v24.3.0` to anything that checks, and semantic-release checks:

```yaml
name: release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: docker
    container:
      image: oven/bun:1.3.14-alpine@sha256:5acc90a93e91ff07bf72aa90a7c9f0fa189765aec90b47bdbf2152d2196383c0
      options: --entrypoint ""
    steps:
      # git + ca-certificates flips checkout to an HTTPS clone; nodejs is
      # what actually runs semantic-release, not bun.
      - run: apk add --no-cache ca-certificates git nodejs

      # fetch-depth: 0 — semantic-release finds the last tag by walking
      # history, and a shallow clone has none, which reads as "never
      # released" the same way a wrong tagFormat does.
      - uses: https://code.forgejo.org/actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false

      - run: bun install --frozen-lockfile

      - name: Check the release credentials are set
        env:
          RELEASE_USER: ${{ secrets.RELEASE_USER }}
          RELEASE_TOKEN: ${{ secrets.RELEASE_TOKEN }}
        run: |
          missing=""
          for pair in "RELEASE_USER:$RELEASE_USER" "RELEASE_TOKEN:$RELEASE_TOKEN"; do
            [ -n "${pair#*:}" ] || missing="$missing ${pair%%:*}"
          done
          if [ -n "$missing" ]; then
            echo "Not releasing. Unset under Settings -> Actions -> Secrets:" >&2
            for name in $missing; do echo "  - $name" >&2; done
            exit 1
          fi

      - name: Release
        env:
          GIT_CREDENTIALS: "${{ secrets.RELEASE_USER }}:${{ secrets.RELEASE_TOKEN }}"
          RELEASE_TOKEN: ${{ secrets.RELEASE_TOKEN }}
        run: bun run release
```

`RELEASE_TOKEN` is a Forgejo access token for the account named in
`RELEASE_USER`, scoped to read and write this repository, stored as an
Actions secret — not a name Forgejo reserves, unlike `FORGEJO_TOKEN`, which
the runner injects automatically into every job and would otherwise
authenticate the release with the wrong credential silently. Add
`release: semantic-release` and `prepare: lefthook install` scripts to this
scaffold's `package.json` alongside the existing bun-tooling devDependencies.

## 2) Dependency updates: Dependabot → Renovate

`.github/dependabot.yml` is GitHub-native — it's GitHub's own dependency
graph raising the pull requests, and it has no Forgejo equivalent. Per
`rules/releases.md`: Renovate's `platform` is `forgejo`, and its
`autodiscover` setting skips anything it can't push to — a repo whose
primary remote is `github.com` is invisible to it, no matter how it's
mirrored.

### If the target Forgejo instance already runs a shared Renovate bot

This is the common case, and it needs **no `renovate.json` in this repo at
all**. This house runs one such bot already, with its
`global-renovate-config.json` setting `"autodiscover": true` — which means
the bot updates every repository its token can see, with no per-repo opt-in
file. Moving this project to an instance like that means asking whoever runs
the bot to give its token access to the new repo (or removing it, to stop
coverage) — nothing to add to the project itself. The bot's own config
already carries the pieces that matter for a repo like this one:
`config:best-practices` (pins dependencies and their digests),
`:semanticCommits`, and — worth knowing before merging your first Renovate
pull request on a bot configured this way — automerge turned on for every
update type, which this repo does not have configured today for Dependabot.

### Standalone case: this repo runs its own Renovate

If there's no shared bot — a personal Forgejo instance, or a project that
wants its own schedule independent of anyone else's — a minimal
`renovate.json` at the repo root:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "platform": "forgejo",
  "extends": ["config:best-practices", ":semanticCommits"]
}
```

(That shared bot's own README notes it was still migrating off an older
`platform: gitea` value at the time of writing, left from before Renovate
added a distinct `forgejo` platform — if `forgejo` is rejected by the
Renovate version in use, `gitea` is the fallback, since Forgejo speaks
Gitea's API for compatibility.)

Renovate detects `pyproject.toml` and `uv.lock` and enables its `uv` manager
automatically — no extra config needed for that, unlike Dependabot, where
this scaffold's own `.github/dependabot.yml` has to name the ecosystem
explicitly:

```yaml
- package-ecosystem: uv
  directory: /
```

Renovate's manager key for the same ecosystem is also `uv` — worth knowing if
you ever need to scope it or turn it off explicitly
(`"uv": { "enabled": false }`), but nothing to add for the default case.

Whichever case applies, keep the same commit-message discipline this repo's
Dependabot config already follows and that `rules/releases.md` calls out
explicitly: dependencies that ship in the built artifact (`uv`) get a `fix:`
prefix so a bump cuts a release, and `github-actions`/CI-only bumps stay
`chore:`/`ci:` so they don't. Renovate's `:semanticCommits` preset needs a
`packageRules` entry (or `commitMessagePrefix` per manager) to reproduce that
split — it does not infer it.

## 3) CI workflows: `.github/workflows/*.yml` → `.forgejo/workflows/*.yml`

Same YAML shape — `on:`, `jobs:`, `steps:`, `uses:`/`run:` — Forgejo Actions
is a compatible implementation of the same spec. The differences that bite:

- **`if:` can read `secrets` at the job level on Forgejo; GitHub Actions
  rejects it.** A production `.forgejo/workflows/ci.yml` in this house gates
  a whole deploy job on
  `if: github.event_name == 'push' && secrets.CLOUDFLARE_API_TOKEN != ''`,
  which is how it stays dormant until credentials exist rather than failing
  every run for a secret nobody's minted yet. On GitHub that same line is a
  syntax error — `secrets` there is only readable inside `env:` or a step,
  never in a job-level `if:`. Don't "fix" a job-level secret check into a
  step-level one on the strength of GitHub's docs; on Forgejo it's already
  correct.
- **Secret names can't start with `GITHUB_`, `FORGEJO_`, or `GITEA_`.**
  Forgejo reserves all three prefixes the way GitHub reserves `GITHUB_`
  alone — `RELEASE_TOKEN`/`RELEASE_USER` in the preceding example are named
  the way they are because
  `FORGEJO_TOKEN` is a name Forgejo already sets automatically, on every job,
  to a token with repository write; a secret with that name would silently
  never be read.
- **Actions need to be reachable from the runner.** GitHub Actions'
  `actions/checkout@v4` short form resolves against `github.com`; a
  self-hosted Forgejo runner instead needs either that host allow-listed for
  outbound fetches, or (the more common answer in practice) the full-URL form
  pointing at Forgejo's own mirror:
  `uses: https://code.forgejo.org/actions/checkout@v4`.
  Third-party actions not mirrored there — `astral-sh/setup-uv`,
  `oven-sh/setup-bun` — need the runner's network policy to permit reaching
  `github.com` directly, or a local mirror set up for them; check what the
  target instance's runner is actually configured to reach before assuming a
  `.github/workflows/*.yml` action reference ports over unchanged.
- **`uv` is not preinstalled on a Forgejo runner any more than it is on a
  fresh development machine.** This repo's own `README.md` says as much for
  local setup —
  `curl -LsSf https://astral.sh/uv/install.sh | sh`, once per machine — and
  `.github/workflows/ci.yml`'s `astral-sh/setup-uv` step is doing the same
  job in CI, pinned to a `version:`. A Forgejo runner needs the equivalent
  step (`astral-sh/setup-uv`, if the runner can reach `github.com`, or the
  curl install run explicitly) in every job that calls `uv sync` or `uv run` —
  it isn't baked into the generic `docker` runner images the way it would be
  in a purpose-built container.
- **Pin container images by digest, same as this repo already does for
  `ghcr.io` and `docker.io` images elsewhere** — `image:tag@sha256:…` — per
  `rules/dependencies.md`. The Forgejo jobs referenced throughout this doc all
  do this (`oven/bun:1.3.14-alpine@sha256:…`); nothing about moving to
  Forgejo changes that rule, it just changes which registry the image most
  likely comes from if the target instance mirrors its own.

A `.forgejo/workflows/ci.yml` translated from this repo's
`.github/workflows/ci.yml` keeps the same jobs (`lint`, `test`, `audit`,
`build`, `prose`, `commits`) and the same commands — only `uses:` lines and
the `if:` shape for anything conditional on a secret need touching.
