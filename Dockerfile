# slim (Debian, glibc), not alpine: the frozen PyInstaller binary this
# builds needs to link against the same glibc floor the .deb/.rpm
# packaging targets — alpine's musl would produce a binary that can't
# run on either.
#
# There's no shipped runtime image here — this template doesn't publish
# a container, only a `pyinstaller` build stage for scripts/build-binary.sh
# to freeze the CLI in. A project stamped from this template that wants
# a runtime image adds a final stage the day it needs one.
FROM ghcr.io/astral-sh/uv:0.12.7@sha256:95f2aa1fe59274951cfe9b0cbc7972e879ff1004bc8945d130a32eb0dbd85945 AS uv
FROM python:3.14-slim-bookworm@sha256:9ab8d9c8514b44f90cf0029dd42fdd7e9e211e639c8b995304cc04568dee900f AS builder

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /build
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/

RUN uv sync --frozen --no-dev --no-editable

# Built with `docker build --target pyinstaller` by scripts/build-binary.sh,
# to freeze the CLI into one binary on the same glibc floor the .deb/.rpm
# packaging targets (see the header comment above).
FROM builder AS pyinstaller
# PyInstaller shells out to objdump to inspect the shared libraries it
# bundles; not part of the slim base image.
RUN apt-get update && apt-get install -y --no-install-recommends binutils=2.40-2 \
  && rm -rf /var/lib/apt/lists/*
RUN uv sync --frozen --no-editable && \
  uv run pyinstaller --onefile --name scaffold-python-cli --distpath /dist /build/.venv/bin/scaffold-python-cli
