import shutil
import subprocess
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


def add_file(path: Path) -> None:
    """
    Add a file to the repository.
    Raises FileExistsError if the file is already in to the repository.
    Raises NotInRepoError if the file path is not within a repository.
    """
    root = find_repo_root()
    if root is None:
        raise NotInRepoError("The current directory is not in a repository")

    abs_path = path.resolve()
    if not abs_path.is_relative_to(root):
        raise NotInRepoError("The file is not within the repository")

    rel_path = abs_path.relative_to(root)
    file_data_dir = root / DATA_DIR / "tree" / rel_path

    if file_data_dir.is_dir():
        raise FileExistsError("File is already added to the repository")

    file_data_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy(rel_path, file_data_dir / "1.ver")


def update_file(path: Path) -> None:
    """
    Create a new version of a file.
    Raises FileExistsError if the file is already in to the repository.
    Raises NotInRepoError if the file path is not within a repository.
    """
    root = find_repo_root()
    if root is None:
        raise NotInRepoError("The current directory is not in a repository")

    abs_path = path.resolve()
    if not abs_path.is_relative_to(root):
        raise NotInRepoError("The file is not within the repository")

    rel_path = abs_path.relative_to(root)
    file_data_dir = root / DATA_DIR / "tree" / rel_path

    # find the latest version in the repository
    version_files = file_data_dir.glob("*")
    versions = sorted([int(p.stem) for p in version_files])
    latest = versions[-1]
    latest_path = file_data_dir / f"{latest}.ver"

    args = ["diff", "-u", str(latest_path), str(abs_path)]
    res = subprocess.run(args, capture_output=True)

    if res.returncode == 0:
        # TOOD: dedicated exception
        raise Exception("File has not changed")
    elif res.returncode > 1:
        error_msg = res.stderr.decode("utf-8")
        raise RuntimeError(f"diff returned {res.returncode}\n{error_msg}")
    else:
        diff = res.stdout.decode("utf-8")

    new_diff_path = file_data_dir / f"{latest + 1}.diff"
    new_diff_path.write_text(diff)


def diff_file(path: Path) -> str | None:
    """
    Show the difference between the working tree and the repository.
    """

    # TODO: handle binary files gracefully

    root = find_repo_root()
    if root is None:
        raise NotInRepoError("The current directory is not in a repository")

    abs_path = path.resolve()
    if not abs_path.is_relative_to(root):
        raise NotInRepoError("The file is not within the repository")

    rel_path = abs_path.relative_to(root)
    file_data_dir = root / DATA_DIR / "tree" / rel_path

    # find the latest version in the repository
    version_files = file_data_dir.glob("*")
    versions = sorted([int(p.stem) for p in version_files])
    latest = versions[-1]
    latest_path = file_data_dir / f"{latest}.ver"

    args = ["diff", "-u", str(latest_path), str(abs_path)]
    res = subprocess.run(args, capture_output=True)
    if res.returncode == 1:
        return res.stdout.decode("utf-8")
    elif res.returncode == 0:
        return None
    else:
        error_msg = res.stderr.decode("utf-8")
        raise RuntimeError(f"diff returned {res.returncode}\n{error_msg}")
