from typer.testing import CliRunner

from scaffold_python_cli.cli import app

runner = CliRunner()


def test_greet_default() -> None:
    result = runner.invoke(app, ["greet"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Hello, World!"


def test_greet_with_name() -> None:
    result = runner.invoke(app, ["greet", "--name", "Ryan"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Hello, Ryan!"
