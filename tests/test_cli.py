import io
import platform
from pathlib import Path

import pytest
from typer.testing import CliRunner

from scaffold_python_cli.cli import app
from scaffold_python_cli.config import VERBOSE_ENV_VAR, config_file_path, load_file_config
from scaffold_python_cli.first_run import maybe_offer_init

runner = CliRunner()


@pytest.fixture(autouse=True)
def isolated_config_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.delenv(VERBOSE_ENV_VAR, raising=False)
    return tmp_path


def test_greet_default() -> None:
    result = runner.invoke(app, ["greet"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Hello, World!"


def test_greet_with_name() -> None:
    result = runner.invoke(app, ["greet", "--name", "Ryan"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Hello, Ryan!"


def test_greet_verbose_flag_adds_build_detail() -> None:
    result = runner.invoke(app, ["--verbose", "greet"])

    assert f"python {platform.python_version()}" in result.stdout


def test_greet_verbose_env_var_adds_build_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(VERBOSE_ENV_VAR, "1")

    result = runner.invoke(app, ["greet"])

    assert f"python {platform.python_version()}" in result.stdout


def test_no_verbose_flag_overrides_a_truthy_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(VERBOSE_ENV_VAR, "1")

    result = runner.invoke(app, ["--no-verbose", "greet"])

    assert result.stdout.strip() == "Hello, World!"


def test_greet_uses_config_file_when_nothing_else_overrides_it(isolated_config_home: Path) -> None:
    path = config_file_path()
    path.parent.mkdir(parents=True)
    path.write_text("verbose = true\n")

    result = runner.invoke(app, ["greet"])

    assert f"python {platform.python_version()}" in result.stdout


def test_init_writes_a_starter_config_file() -> None:
    result = runner.invoke(app, ["init"])

    assert result.exit_code == 0
    assert config_file_path().exists()
    assert load_file_config().verbose is False


def test_init_refuses_to_overwrite_an_existing_config_file() -> None:
    runner.invoke(app, ["init"])

    result = runner.invoke(app, ["init"])

    assert result.exit_code != 0
    assert "already exists" in str(result.exception)


def test_init_force_overwrites_an_existing_config_file() -> None:
    runner.invoke(app, ["init"])
    config_file_path().write_text("verbose = true\n")

    result = runner.invoke(app, ["init", "--force"])

    assert result.exit_code == 0
    assert load_file_config().verbose is False


def test_yes_flag_writes_the_config_file_without_prompting() -> None:
    runner.invoke(app, ["--yes", "greet"])

    assert config_file_path().exists()


def test_maybe_offer_init_skips_a_run_with_an_existing_config_file() -> None:
    config_file_path().parent.mkdir(parents=True)
    config_file_path().write_text("verbose = false\n")
    stderr = io.StringIO()

    maybe_offer_init(
        stdin=io.StringIO(),
        stdout=io.StringIO(),
        stderr=stderr,
        is_terminal=False,
        skip_prompt=False,
    )

    assert stderr.getvalue() == ""


def test_maybe_offer_init_skips_a_run_with_the_env_var_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(VERBOSE_ENV_VAR, "0")
    stderr = io.StringIO()

    maybe_offer_init(
        stdin=io.StringIO(),
        stdout=io.StringIO(),
        stderr=stderr,
        is_terminal=False,
        skip_prompt=False,
    )

    assert stderr.getvalue() == ""


def test_maybe_offer_init_warns_on_stderr_when_not_a_terminal() -> None:
    stderr = io.StringIO()

    maybe_offer_init(
        stdin=io.StringIO(),
        stdout=io.StringIO(),
        stderr=stderr,
        is_terminal=False,
        skip_prompt=False,
    )

    assert "scaffold-python-cli init" in stderr.getvalue()


def test_maybe_offer_init_writes_the_config_file_when_skip_prompt() -> None:
    stdout = io.StringIO()

    maybe_offer_init(
        stdin=io.StringIO(),
        stdout=stdout,
        stderr=io.StringIO(),
        is_terminal=False,
        skip_prompt=True,
    )

    assert config_file_path().exists()
    assert "Wrote" in stdout.getvalue()


def test_maybe_offer_init_writes_the_config_file_on_a_yes_answer() -> None:
    maybe_offer_init(
        stdin=io.StringIO("y\n"),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        is_terminal=True,
        skip_prompt=False,
    )

    assert config_file_path().exists()


def test_maybe_offer_init_does_nothing_on_a_no_answer() -> None:
    maybe_offer_init(
        stdin=io.StringIO("n\n"),
        stdout=io.StringIO(),
        stderr=io.StringIO(),
        is_terminal=True,
        skip_prompt=False,
    )

    assert not config_file_path().exists()
