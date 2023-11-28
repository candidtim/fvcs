import sys
from pathlib import Path

import click

from .repo import (NotInRepoError, add_file, diff_file, find_repo_root,
                   init_repo, update_file)


EXIT_NOT_IN_REPO = 1
EXIT_ALREADY_ADDED = 2


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
        sys.exit(EXIT_ALREADY_ADDED)


@main.command()
@click.argument("glob")
def add(glob: str):
    # TODO: treat the argument as a glob pattern
    try:
        add_file(Path(glob))
    except FileExistsError:
        click.echo(f"File {glob} is already added to the repository")
        sys.exit(EXIT_ALREADY_ADDED)
    except NotInRepoError:
        click.echo(f"File {glob} is not within a repository")
        sys.exit(EXIT_NOT_IN_REPO)


@main.command()
@click.argument("glob")
def update(glob: str):
    # TODO: treat the argument as a glob pattern
    try:
        update_file(Path(glob))
    except NotInRepoError:
        click.echo(f"File {glob} is not within a repository")
        sys.exit(EXIT_NOT_IN_REPO)
    except Exception as e:
        click.echo(e)
        sys.exit(EXIT_ALREADY_ADDED)


@main.command()
@click.argument("path")
def diff(path: str):
    try:
        diff = diff_file(Path(path))
        if diff is None:
            click.echo(f"File {path} is not modified")
        else:
            click.echo(diff)
    except NotInRepoError:
        click.echo(f"File {path} is not in a repository")
        sys.exit(EXIT_NOT_IN_REPO)
