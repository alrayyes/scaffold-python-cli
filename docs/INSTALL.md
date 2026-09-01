# Installing scaffold-python-cli

Every method below installs the `scaffold-python-cli` command. Pick
whichever matches your system; none of them need any of the others.

A project stamped from this template inherits every packaging path
described here as-is — rename `scaffold-python-cli` to the project's own
name throughout (`nfpm.yaml`, `PKGBUILD`, `flake.nix`, the workflows under
`.github/workflows/`, and this file) the same day the `greet` command gets
replaced.

## Arch Linux (AUR)

```sh
paru -S scaffold-python-cli
```

An AUR helper (`paru`, `yay`, or similar) is the easiest path. Without
one:

```sh
git clone https://aur.archlinux.org/scaffold-python-cli.git
cd scaffold-python-cli
makepkg -si
```

Builds for real against Arch's own `python-*` packages — see the
[`PKGBUILD`](../PKGBUILD) in this repo for the exact dependencies (kept
here for reference and review; the actual AUR package lives in its own
git repo, updated by this project's release job).

## Nix

```sh
nix run github:alrayyes/scaffold-python-cli -- --help
```

Or install it onto a profile:

```sh
nix profile install github:alrayyes/scaffold-python-cli
```

Builds for real, straight off this repo's own [`flake.nix`](../flake.nix)
— no hosted binary cache, so a first install builds from source. Any
commit in the repo's history can be built this way, not just a tagged
release: replace `github:alrayyes/scaffold-python-cli` with
`github:alrayyes/scaffold-python-cli/<ref>` to pin one.

## Debian, Ubuntu and other `.deb`-based distros

Download the `.deb` from the
[latest release](https://github.com/alrayyes/scaffold-python-cli/releases/latest)
and install it:

```sh
curl -LO https://github.com/alrayyes/scaffold-python-cli/releases/latest/download/scaffold-python-cli_VERSION_amd64.deb
sudo dpkg -i scaffold-python-cli_VERSION_amd64.deb
```

Replace `VERSION` with the version you downloaded (matching the filename
on the release page). No separate Python install needed — the package
bundles everything it depends on.

## Fedora, RHEL and other `.rpm`-based distros

Download the `.rpm` from the
[latest release](https://github.com/alrayyes/scaffold-python-cli/releases/latest)
and install it:

```sh
curl -LO https://github.com/alrayyes/scaffold-python-cli/releases/latest/download/scaffold-python-cli-VERSION-1.x86_64.rpm
sudo rpm -i scaffold-python-cli-VERSION-1.x86_64.rpm
```

Replace `VERSION` with the version you downloaded. Same as the `.deb`:
no separate Python install needed.

## Verifying a downloaded `.deb`/`.rpm`

Every release asset carries a build provenance attestation tying it to
the GitHub Actions run that produced it:

```sh
gh attestation verify scaffold-python-cli_VERSION_amd64.deb --repo alrayyes/scaffold-python-cli
```

## From a checkout, or without a package manager

```sh
git clone https://github.com/alrayyes/scaffold-python-cli.git
cd scaffold-python-cli
uv sync
uv run scaffold-python-cli --help
```

Or install the command directly without keeping the checkout around —
this project isn't published to PyPI, so install straight from the repo:

```sh
pipx install git+https://github.com/alrayyes/scaffold-python-cli.git
```

`pip install` works the same way in place of `pipx` if you'd rather
manage the virtual environment yourself.
