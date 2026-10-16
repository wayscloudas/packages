"""Regression tests for ``lang/python/micropython-lib/install.py``.

SonarQube reports ``pythonsecurity:S2083`` on the unvalidated ``os.path.join`` in
``install()``. The names it joins — the package name from ``index.json``, then the file
name and file hash from each package's ``latest.json`` — are data read out of the input
tree, not paths the script chose. A name containing ``..``, or an absolute path, decides
where the script reads and writes.

The traversal tests below fail on the unfixed script: they assert that the refusal
happens, and the unfixed script instead reads or writes outside the directories it was
given. The first test fails rather than passing vacuously if the happy path ever stops
working.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL_PY = REPO_ROOT / "lang/python/micropython-lib/install.py"
MPY_VERSION = "6"
PAYLOAD = b"compiled-payload"
FILE_HASH = "ab" * 32
FILE_NAME = "os/__init__.mpy"


def _load_install_module():
    spec = importlib.util.spec_from_file_location("micropython_lib_install", INSTALL_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


install = _load_install_module()


def build_input(input_root: Path, package_name: str = "os", file_name: str = FILE_NAME, file_hash: str = FILE_HASH) -> Path:
    """Write the smallest input tree ``install()`` accepts: one package holding one file."""
    (input_root / "package" / MPY_VERSION / package_name).mkdir(parents=True, exist_ok=True)
    (input_root / "index.json").write_text(
        json.dumps({"packages": [{"name": package_name}]}), encoding="utf-8"
    )
    (input_root / "package" / MPY_VERSION / package_name / "latest.json").write_text(
        json.dumps({"hashes": [[file_name, file_hash]]}), encoding="utf-8"
    )
    blob = input_root / "file" / file_hash[:2] / file_hash
    blob.parent.mkdir(parents=True, exist_ok=True)
    blob.write_bytes(PAYLOAD)
    return input_root


def test_a_valid_tree_is_installed(tmp_path: Path) -> None:
    input_root = build_input(tmp_path / "input")
    output_root = tmp_path / "output"

    install.install(str(input_root), MPY_VERSION, str(output_root))

    assert (output_root / FILE_NAME).read_bytes() == PAYLOAD


def test_a_package_name_cannot_read_outside_the_input_directory(tmp_path: Path) -> None:
    # `input/package/6/../../../outside/latest.json` resolves to `tmp_path/outside/latest.json`.
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "latest.json").write_text(
        json.dumps({"hashes": [[FILE_NAME, FILE_HASH]]}), encoding="utf-8"
    )
    input_root = build_input(tmp_path / "input", package_name="../../../outside")

    with pytest.raises(ValueError):
        install.install(str(input_root), MPY_VERSION, str(tmp_path / "output"))


def test_a_file_name_cannot_write_outside_the_output_directory(tmp_path: Path) -> None:
    input_root = build_input(tmp_path / "input", file_name="../escaped.mpy")

    with pytest.raises(ValueError):
        install.install(str(input_root), MPY_VERSION, str(tmp_path / "output"))

    assert not (tmp_path / "escaped.mpy").exists()


def test_an_absolute_file_name_is_refused(tmp_path: Path) -> None:
    target = tmp_path / "absolute.mpy"
    input_root = build_input(tmp_path / "input", file_name=str(target))

    with pytest.raises(ValueError):
        install.install(str(input_root), MPY_VERSION, str(tmp_path / "output"))

    assert not target.exists()


def test_a_file_hash_cannot_read_outside_the_input_directory(tmp_path: Path) -> None:
    # `input/file/../../outside/blob` resolves to `tmp_path/outside/blob`.
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "blob").write_bytes(PAYLOAD)

    input_root = tmp_path / "input"
    (input_root / "package" / MPY_VERSION / "os").mkdir(parents=True)
    # `input/file/` has to exist for the pre-fix script to walk out of it: without the
    # directory the escape would fail with ENOENT instead of reading the planted file.
    (input_root / "file").mkdir()
    (input_root / "index.json").write_text(
        json.dumps({"packages": [{"name": "os"}]}), encoding="utf-8"
    )
    (input_root / "package" / MPY_VERSION / "os" / "latest.json").write_text(
        json.dumps({"hashes": [[FILE_NAME, "../outside/blob"]]}), encoding="utf-8"
    )

    with pytest.raises(ValueError):
        install.install(str(input_root), MPY_VERSION, str(tmp_path / "output"))
