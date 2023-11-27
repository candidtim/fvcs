from pathlib import Path

DATA_DIR = ".fvcs"


class NotInRepoError(Exception):
    pass


def _is_fs_root(path: Path) -> bool:
    return path.parent == path


def _is_repo_root(path: Path) -> bool:
    return (path / DATA_DIR).is_dir()


def find_repo_root() -> Path | None:
    """
    Recursively search for the repository root up the directory tree starting
    from the current directory.
    """
    cwd = Path.cwd()
    for path in [cwd, *cwd.parents]:
        if _is_repo_root(path):
            return path
    return None


def init_repo() -> Path:
    """
    Initialize a new repository in the current directory.
    Raises FileExistsError if the repository already exists.
    """
    repo_path = Path.cwd() / DATA_DIR
    repo_path.mkdir(parents=True, exist_ok=False)
    return repo_path
