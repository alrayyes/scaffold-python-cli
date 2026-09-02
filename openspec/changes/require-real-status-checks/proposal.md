# Require real status checks

## Why

Branch protection on `main` had no `required_status_checks` set at all,
so `gh pr merge --auto` in `dependabot-auto-merge.yml` and
`release-auto-merge.yml` only waited on GitHub's general merge
eligibility, not on this repo's own CI passing.

## What changes

`required_status_checks` is now `strict: true`, with this repo's real,
pull-request-triggered check names: `aur`, `build`, `check`, `commits`,
`lint`, `mechanics`, `nix`, `package-linux / build-and-test`, `prose`,
`secrets`, `style`, `test` Names came from an actual pull request, not
guessed from workflow job keys.
`required_approving_review_count` was already `0` and stays that way.

## Capabilities

No capability spec changes -- branch-protection plumbing only.
`skip_specs: true`.

## Impact

Changed: branch protection on `main`, a repo setting applied directly via
the GitHub API. Not a file, so not part of this pull request's diff.
