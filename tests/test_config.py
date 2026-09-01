from pathlib import Path

import pytest

from scaffold_python_cli.config import (
    SecretCommandError,
    config_file_path,
    load_file_config,
    resolve_secret,
)


def test_resolve_secret_returns_the_literal_when_no_command_is_set() -> None:
    assert resolve_secret("shh", "") == "shh"


def test_resolve_secret_runs_the_command_and_uses_its_stdout() -> None:
    assert resolve_secret("shh", "echo from-command") == "from-command"


def test_resolve_secret_trims_exactly_one_trailing_newline() -> None:
    # two newlines in, one trimmed -- not every trailing newline the
    # command happens to print.
    assert resolve_secret("", "printf 'value\\n\\n'") == "value\n"


def test_resolve_secret_command_wins_over_a_literal_when_both_are_set() -> None:
    assert resolve_secret("literal", "echo from-command") == "from-command"


def test_resolve_secret_raises_on_a_failing_command() -> None:
    with pytest.raises(SecretCommandError):
        resolve_secret("", "exit 1")


def test_resolve_secret_never_falls_back_to_the_literal_on_a_failing_command() -> None:
    # a failing command must error, not quietly resolve to "" or to
    # whatever literal happened to be sitting alongside it.
    with pytest.raises(SecretCommandError, match="exited 1"):
        resolve_secret("fallback-that-must-not-be-used", "exit 1")


def test_resolve_secret_runs_through_the_shell() -> None:
    # a pipeline, not just a bare executable -- same as restic's
    # --password-command, msmtp's passwordeval, Borg's BORG_PASSCOMMAND.
    assert resolve_secret("", "echo shh | tr a-z A-Z") == "SHH"


@pytest.mark.parametrize("field", ["api_token", "api_token_command"])
def test_load_file_config_rejects_a_non_string_secret_field(
    field: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    path = config_file_path()
    path.parent.mkdir(parents=True)
    path.write_text(f"{field} = 12345\n")

    with pytest.raises(ValueError, match=f"{field} must be a string"):
        load_file_config()
