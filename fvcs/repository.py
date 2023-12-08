import shutil
from functools import cached_property
from pathlib import Path
from typing import Optional

from .diff import make_diff, apply_patch


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
            msg = f"The repository already exists in {repo.root}"
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
        self.name = self.path.name
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

    @property
    def _latest_path(self) -> Path:
        # notably, latest is not in the same directory as the diff files
        # avoids confustions in case the original file name itself is "latest"
        return self._data_dir / "latest"

    @property
    def _diff_dir(self) -> Path:
        return self._data_dir / "versions"

    def exists(self) -> bool:
        return self._data_dir.is_dir()

    def create(self) -> None:
        """
        Add a file to the repository.
        Raises RedundantOperationError if the file is already in the repository.
        Raises NotInRepositoryError if the file path is not within a repository.
        """
        if self.exists():
            msg = f"{self} is already in the repository"
            raise RedundantOperationError(msg)

        self._data_dir.mkdir(parents=True, exist_ok=False)
        self._diff_dir.mkdir(parents=True, exist_ok=False)
        shutil.copy(self.path, self._latest_path)

    def update(self) -> int:
        """Create a new version of the file based on the working copy"""
        next_version = self.versions[-1] + 1 if self.versions else 1
        diff = make_diff(self.name, self.path, self._latest_path)  # reverse diff
        if diff is None:
            raise NoChangeError(f"{self} is not modified")

        diff_path = self._diff_dir / f"{next_version}.diff"
        diff_path.write_text(diff)
        shutil.copy(self.path, self._latest_path)

        return next_version

    def diff(self) -> str | None:
        if not self.exists():
            raise NotInRepositoryError(f"{self} is not in the repository")
        return make_diff(self.name, self._latest_path, self.path)

    def restore(self, version: int, force: bool) -> None:
        diff = make_diff(self.name, self._latest_path, self.path)
        if diff is not None and not force:
            raise FileChangedError(f"{self} is modified")

        if version not in self.versions:
            raise Exception(f"{self} has no version {version}")

        patch_versions = reversed([v for v in self.versions if v >= version])
        patches = [self._diff_dir / f"{v}.diff" for v in patch_versions]
        base = self._data_dir / self.name
        shutil.copy(self._data_dir / "latest", base)
        for p in patches:
            apply_patch(base, p)
        shutil.move(base, self.path)

    @cached_property
    def versions(self) -> list[int]:
        diff_files = self._diff_dir.glob("*.diff")
        versions = sorted([int(p.stem) for p in diff_files])
        return versions

    def __str__(self) -> str:
        return str(self.path)
