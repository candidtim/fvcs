import sys
from pathlib import Path

import click

from .repository import (FileChangedError, NoChangeError, NotInRepositoryError,
                         RedundantOperationError, Repository)

EXIT_NOT_IN_REPO = 1
EXIT_REDUNDANT_OPERATION = 2
EXIT_USAGE_ERROR = 3


@click.group()
def main():
    pass


@main.command()
def init():
    try:
        repo = Repository.create()
        click.echo(f"The repository is initialized in {repo.root}")
    except RedundantOperationError as err:
        click.echo(str(err))
        sys.exit(EXIT_REDUNDANT_OPERATION)


@main.command()
@click.argument("glob")
def add(glob: str):
    # TODO: treat the argument as a glob pattern
    path = Path(glob)
    try:
        repo = Repository.find_or_fail()
        vfile = repo.find_file(path)
        vfile.create()
        click.echo(f"Added {vfile} to the repository")
    except NotInRepositoryError as err:
        click.echo(str(err))
        sys.exit(EXIT_NOT_IN_REPO)
    except RedundantOperationError as err:
        click.echo(str(err))
        sys.exit(EXIT_REDUNDANT_OPERATION)


@main.command()
@click.argument("glob")
def update(glob: str):
    # TODO: treat the argument as a glob pattern
    path = Path(glob)
    try:
        repo = Repository.find_or_fail()
        vfile = repo.find_file(path)
        version = vfile.update()
        click.echo(f"Updated {vfile} (previous version: {version})")
    except NotInRepositoryError as err:
        click.echo(str(err))
        sys.exit(EXIT_NOT_IN_REPO)
    except NoChangeError as err:
        click.echo(str(err))
        sys.exit(EXIT_REDUNDANT_OPERATION)


@main.command()
@click.argument("path")
def diff(path: str):
    try:
        repo = Repository.find_or_fail()
        vfile = repo.find_file(Path(path))
        diff = vfile.diff()
        if diff is None:
            click.echo(f"{vfile} is not modified")
        else:
            click.echo(diff)
    except NotInRepositoryError as err:
        click.echo(str(err))
        sys.exit(EXIT_NOT_IN_REPO)


@main.command()
@click.argument("path")
@click.argument("version", type=int)
@click.option("--force", "-f", is_flag=True, default=False)
def get(path: str, version: int, force: bool):
    try:
        repo = Repository.find_or_fail()
        vfile = repo.find_file(Path(path))
        vfile.restore(version, force)
        click.echo(f"Restored {vfile} to version {version}")
    except NotInRepositoryError as err:
        click.echo(str(err))
        sys.exit(EXIT_NOT_IN_REPO)
    except FileChangedError as err:
        click.echo(str(err))
        sys.exit(EXIT_USAGE_ERROR)


@main.command()
@click.argument("path")
def log(path: str):
    try:
        repo = Repository.find_or_fail()
        vfile = repo.find_file(Path(path))
        for v in vfile.versions:
            print(v)
    except NotInRepositoryError as err:
        click.echo(str(err))
        sys.exit(EXIT_NOT_IN_REPO)
