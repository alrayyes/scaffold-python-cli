"""The Typer app. One example command, `greet`, so the whole chain — CLI,
tests, hooks, CI — has something real to run against. Replace it with your
first real command and delete this comment.
"""

import typer

app = typer.Typer(help="scaffold-python-cli: a Typer command-line tool.")


@app.callback()
def callback() -> None:
    """scaffold-python-cli: a Typer command-line tool.

    An empty callback, not a no-op — its only job is stopping Typer/Click
    from collapsing a single-command app into a bare one, so `greet` stays
    a real subcommand (`scaffold-python-cli greet`) instead of the whole
    program.
    """


@app.command()
def greet(name: str = typer.Option("World", "--name", help="Who to greet.")) -> None:
    """Print a greeting."""
    typer.echo(f"Hello, {name}!")


def main() -> None:
    app()
