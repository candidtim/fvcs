"""Convenincy wrappers around diff and patch"""

import subprocess
from pathlib import Path


def make_diff(label: str, left: Path, right: Path) -> str | None:
    """
    Run diff on two files and return the unified diff output. Both files have
    the same given label in the produced diff.
    """
    args = [
        "diff",
        "--unified",
        "--label",
        label,
        "--label",
        label,
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


def apply_patch(orig: Path, diff: Path) -> None:
    """
    Apply a patch on the original file in place. Side-effect only.
    """
    args = [
        "patch",
        "--unified",
        "--remove-empty-files",
        # "--directory",
        # str(work_dir),
        "--input",
        str(diff),
        str(orig),
    ]
    print(args)
    res = subprocess.run(args, capture_output=True)
    if res.returncode != 0:
        err_msg = res.stderr.decode("utf-8")
        raise Exception(f"patch returned {res.returncode}\n{err_msg}")
