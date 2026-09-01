{
  description = "GitHub template for a Python/uv/Typer command-line tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        # nixos-unstable's python3 is already 3.14, but its uv-build
        # (0.11.28 as of writing) is older than this project's own
        # `[build-system] requires = ["uv-build>=0.12.5,<0.13"]` —
        # confirmed live on movie-planner (this scaffold's reference
        # implementation): `buildPythonApplication`'s pypa build hook
        # enforces that range and refuses the older one outright
        # ("Unmet dependencies ... found: 0.11.28"). Overridden here to
        # the exact version this repo already pins uv itself to
        # elsewhere, built the same way nixpkgs' own uv-build derivation
        # is (rustPlatform + maturin), just at a newer tag.
        python3 = pkgs.python3.override {
          packageOverrides = _self: super: {
            uv-build = super.uv-build.overrideAttrs (old: rec {
              version = "0.12.7";
              src = pkgs.fetchFromGitHub {
                owner = "astral-sh";
                repo = "uv";
                tag = version;
                hash = "sha256-RprHadjzR5LsiYYhryIGOiIQkRKVWJwyE63UXrzN62g=";
              };
              cargoDeps = pkgs.rustPlatform.fetchCargoVendor {
                inherit (old) pname;
                inherit version src;
                hash = "sha256-zEZNPEI7GLkWJ49jd8jS+VsuijaW8/ZMWyus3VFcZPo=";
              };
            });
          };
        };
        # Kept in sync with pyproject.toml's [project].version by hand —
        # release-please owns that file, not this one.
        version = "0.2.0";

        # Not in nixpkgs at all (confirmed: no click-man attribute in
        # python3Packages) — a small enough package (its only
        # dependency is click, already in nixpkgs) to vendor directly
        # rather than drop the man-page generation it enables.
        clickMan = python3.pkgs.buildPythonPackage {
          pname = "click-man";
          version = "0.5.1";
          format = "wheel";
          src = pkgs.fetchurl {
            url = "https://files.pythonhosted.org/packages/e1/37/34e03579eb583a587edba458599af6d82715a617e685dbe2ff30e4238930/click_man-0.5.1-py3-none-any.whl";
            sha256 = "ed63caf6d6bf04f2b1fb198a1a764daea9785ad29f303b2962418a417541a6ce";
          };
          propagatedBuildInputs = [ python3.pkgs.click ];
          doCheck = false;
        };
      in
      {
        packages.default = python3.pkgs.buildPythonApplication {
          pname = "scaffold-python-cli";
          inherit version;
          pyproject = true;

          src = ./.;

          # This project's own build backend (astral-sh/uv's uv_build),
          # same as every other packaging path in this repo.
          build-system = [ python3.pkgs.uv-build ];

          # Depends on nixpkgs' own versions of these rather than
          # vendoring pyproject.toml's exact pins — nixpkgs versions its
          # Python packages itself, the same tradeoff the AUR
          # PKGBUILD's depends=() already makes for the same reason.
          dependencies = with python3.pkgs; [
            platformdirs
            tomli-w
            typer
          ];

          # The wheel's own metadata carries pyproject.toml's exact
          # pins ("typer==0.27.1", "platformdirs==4.11.5"), and
          # pythonRuntimeDepsCheckHook checks the built wheel against
          # those literally — confirmed live: nixos-unstable's own
          # typer (0.25.1) and platformdirs (4.10.0) both fail that
          # check outright ("X==Y not satisfied by version Z") despite
          # being exactly what `dependencies` above asks Nix to
          # provide. Relaxing the version constraint for these is what
          # nixpkgs itself recommends for an upstream exact-pin a
          # distro's own package versioning doesn't track lockstep —
          # the same tradeoff `dependencies` already makes on nixpkgs'
          # behalf, just telling the runtime check about it too.
          pythonRelaxDeps = [
            "platformdirs"
            "typer"
          ];

          nativeBuildInputs = [
            clickMan
            pkgs.installShellFiles
          ];

          # One man page per command and subcommand, generated straight
          # from the just-installed package — the same click-man
          # approach scripts/generate-man.sh uses for the .deb/.rpm/AUR
          # paths, just invoked directly since scripts/generate-man.sh
          # itself is uv-specific and needs network access Nix's
          # sandboxed build doesn't have.
          postInstall = ''
            PYTHONPATH="$out/${python3.sitePackages}:$PYTHONPATH" ${python3.interpreter} -c "
            import datetime
            import typer.main
            from click_man.core import write_man_pages
            from scaffold_python_cli.cli import app
            write_man_pages('scaffold-python-cli', typer.main.get_command(app), version='${version}', target_dir='.', date=datetime.date.today())
            "
            for page in ./*.1; do
              installManPage "$page"
            done
          '';

          # CI's own test job already runs the suite outside Nix; this
          # build only needs to prove the package itself installs and
          # its man pages generate, the same scope every other
          # packaging path here has.
          doCheck = false;

          meta = {
            description = "GitHub template for a Python/uv/Typer command-line tool";
            homepage = "https://github.com/alrayyes/scaffold-python-cli";
            mainProgram = "scaffold-python-cli";
          };
        };

        apps.default = flake-utils.lib.mkApp { drv = self.packages.${system}.default; };
      }
    );
}
