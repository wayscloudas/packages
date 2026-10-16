"""Regression tests for the Python helpers that ship with the packages feed.

The helper scripts under ``lang/python/`` are executed by the OpenWrt build system on a
buildroot, not here. Nothing in this repository imports them, so a syntax error would
first be noticed in a device build. These tests read them, and the tests added alongside
a fix exercise them.

Run through ``docs/sonar/local-check.sh`` while GitHub Actions is down.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def tracked_python_files() -> list[Path]:
    """Every ``*.py`` file tracked by git, as an absolute path."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "*.py"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [REPO_ROOT / name for name in result.stdout.split("\0") if name]


TRACKED_PYTHON_FILES = tracked_python_files()


def test_the_repository_still_has_python_files() -> None:
    # Without this, a broken discovery would make the compile check below pass on an
    # empty list. A check that cannot fail is not a check.
    assert TRACKED_PYTHON_FILES, "git ls-files found no *.py file; the check below is vacuous"


@pytest.mark.parametrize(
    "path",
    TRACKED_PYTHON_FILES,
    ids=[str(path.relative_to(REPO_ROOT)) for path in TRACKED_PYTHON_FILES],
)
def test_python_file_is_syntactically_valid(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    compile(source, str(path), "exec")
