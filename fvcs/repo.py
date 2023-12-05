import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple


class FvcsError(Exception):
    pass


class NotInRepositoryError(FvcsError):
    pass


class RedundantOperationError(FvcsError):
    pass


class NoChangeError(FvcsError):
    pass


class FileChangedError(FvcsError):
    pass


class Repository:
    DATA_DIR = ".fvcs"

    def __init__(self, path: Path):
        # must not be used directly, use find() or find_or_fail() to
        # guarantee that Repository instances are in valid states
        self.root = path.resolve()

    @classmethod
    def find(cls) -> Optional["Repository"]:
        """
        Find the repository anywhere from current directory and up.
        Returns None if no repository is found.
        """
        cwd = Path.cwd()
        for path in [cwd, *cwd.parents]:
            candidate = path / Repository.DATA_DIR
            if candidate.is_dir():
                return Repository(path)
        return None

    @classmethod
    def find_or_fail(cls) -> "Repository":
        """
        Same as find() but raises NotInRepositoryError if the repository is not
        found in the current directory or any of its parents.
        """
        repo = Repository.find()
        if repo is None:
            msg = "Current directory is not in a repository"
            raise NotInRepositoryError(msg)
        return repo

    @classmethod
    def create(cls) -> "Repository":
        """
        Initialize a new repository in the current directory.
        Raises RedundantOperationError if the repository already exists in the
        current directory or any of its parents.
        """
        repo = Repository.find()
        if repo is not None:
            msg = f"Repository already exists at {repo.root}"
            raise RedundantOperationError(msg)
        else:
            repo = Repository(Path.cwd())
            repo._data_dir.mkdir(parents=True, exist_ok=False)
            return repo

    @property
    def _data_dir(self) -> Path:
        return self.root / Repository.DATA_DIR

    def find_file(self, path: Path) -> "VersionedFile":
        return VersionedFile._get(path, self)


class VersionedFile:
    def __init__(self, path: Path, repo: Repository):
        # must not be used directly, use Repository.find_file or _get to
        # guarantee that VersionedFile instances are in valid states
        self.path = path
        self.repo = repo

    @classmethod
    def _get(cls, path: Path, repo: Repository) -> "VersionedFile":
        abs_path = path.resolve()
        if not abs_path.is_relative_to(repo.root):
            raise NotInRepositoryError(f"{path} is not within the repository")

        rel_path = abs_path.relative_to(repo.root)
        return VersionedFile(rel_path, repo)

    @property
    def _data_dir(self) -> Path:
        return self.repo._data_dir / "tree" / self.path

    def exists(self) -> bool:
        return self._data_dir.is_dir()

    def create(self) -> None:
        """
        Add a file to the repository.
        Raises RedundantOperationError if the file is already in to the repository.
        Raises NotInRepositoryError if the file path is not within a repository.
        """
        if self.exists():
            msg = f"{self} is already in the repository"
            raise RedundantOperationError(msg)

        self._data_dir.mkdir(parents=True, exist_ok=False)
        self._new_version(prev_content=None)

    def new_version(self) -> None:
        self._new_version(prev_content=self._latest())

    def _new_version(self, prev_content: Path | None) -> None:
        """Create a new version of the file based on the working copy"""
        next_version = self.versions[-1] + 1 if self.versions else 1
        diff = make_diff(prev_content, self.path)
        if diff is None:
            raise NoChangeError(f"{self} has not changed")

        new_diff_path = self._data_dir / f"{next_version}.diff"
        new_diff_path.write_text(diff)

    def diff(self) -> str | None:
        # FIXME: this check should be pretty much everywhere, but it may thus become redundant
        if not self.exists():
            raise NotInRepositoryError(f"{self} is not in the repository")
        return make_diff(self._latest(), self.path)

    def restore(self, version: int, force: bool) -> None:
        diff = make_diff(self._latest(), self.path)
        if diff is not None and not force:
            raise FileChangedError(f"{self} has chaanged")
        else:
            shutil.copyfile(self._as_of(version), self.path)

    def _as_of(self, version: int) -> Path:
        if version not in self.versions:
            raise Exception(f"{self} has no version {version}")

        diffs = [self._data_dir / f"{v}.diff" for v in self.versions if v <= version]
        return patch(diffs)

    def _latest(self) -> Path:
        return self._as_of(self.versions[-1])

    @property
    def versions(self) -> list[int]:
        diff_files = self._data_dir.glob("*.diff")
        versions = sorted([int(p.stem) for p in diff_files])
        return versions

    def __str__(self) -> str:
        return str(self.path)


def make_diff(left: Path | None, right: Path | None) -> str | None:
    """
    Run diff on two files and return the unified diff output.
    Works with text files only.
    Accepts None on left or right to indicate an empty file (diff will reflect
    all lines added or removed).
    """
    # TODO: handle binary files gracefully

    def normalize_argument(path: Path | None) -> Tuple[Path, str]:
        if path is None:
            return Path("/dev/null"), "/dev/null"
        else:
            return path, str(path.name)

    left, left_label = normalize_argument(left)
    right, right_label = normalize_argument(right)

    args = [
        "diff",
        "--unified",
        "--label",
        left_label,
        "--label",
        right_label,
        str(left),
        str(right),
    ]
    res = subprocess.run(args, capture_output=True)
    if res.returncode > 1:
        err_msg = res.stderr.decode("utf-8")
        raise Exception(f"diff returned {res.returncode}\n{err_msg}")
    elif res.returncode == 0:
        return None
    else:
        return res.stdout.decode("utf-8")


def patch(diffs: list[Path]) -> Path:
    """
    Apply a list of diffs in a temporary directory and return the path of the
    resulting filof the resulting file.
    """
    # FIXME: this assumes that all diffs apply to the same file, which is how
    # add/update are designed, but is fragile; at least assert along the way
    # FIXME: clean up the temporary directory
    tmp_dir_path = tempfile.mkdtemp()
    args = [
        "patch",
        "--unified",
        "--remove-empty-files",
        "--directory",
        str(tmp_dir_path),
    ]
    for diff in diffs:
        iargs = args + ["--input", str(diff)]
        print("$ " + " ".join(iargs))
        res = subprocess.run(iargs, cwd=Path.cwd(), capture_output=True)
        if res.returncode != 0:
            err_msg = res.stderr.decode("utf-8")
            raise Exception(f"patch returned {res.returncode}\n{err_msg}")
    return Path(tmp_dir_path) / diffs[0].name
