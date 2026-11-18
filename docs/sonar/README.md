# Verification in this repository

The organisation's SonarQube Cloud campaign and its register are tracked in the private infrastructure repository. This public repository keeps only the build and test surface:

- `pytest.ini` points `pytest` at `tests/`.
- `tests/test_python_sources.py` compiles every tracked `*.py` file and fails when discovery finds no files.

The internal campaign baseline, finding register and triage rules are not published here.

## Limits

The C and C++ sources under `*/src/` are built by the OpenWrt build system only. Nothing in this repository compiles them, so a change there is reviewed, not built. Coverage is not measured here; a green gate is not evidence that the new code is tested.
