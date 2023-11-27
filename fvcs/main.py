import click

from .fs import find_repo_root, init_repo


@click.group()
def main():
    pass


@main.command()
def init():
    try:
        repo_root = init_repo()
        click.echo(f"The repository is initialized in {repo_root}")
    except FileExistsError:
        repo_root = find_repo_root()
        click.echo(f"The repository is already initialized in {repo_root}")
        click.exit(1)


@main.command()
@click.argument("glob")
def add(glob):
    raise NotImplementedError()
