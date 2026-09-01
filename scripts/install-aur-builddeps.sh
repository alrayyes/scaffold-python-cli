#!/usr/bin/env bash
# python-click-man isn't in Arch's official repos, only the AUR —
# pacman can't install it directly, so this builds and installs it
# from source the same way an AUR helper would. Shared by the CI dry
# run and the release job so a real `makepkg` build isn't the only one
# exercising this PKGBUILD.
set -euo pipefail

git clone --depth 1 https://aur.archlinux.org/python-click-man.git /tmp/python-click-man
(cd /tmp/python-click-man && makepkg -si --noconfirm --nocheck)
