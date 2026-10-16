# SonarQube in `wayscloudas/packages`

The process is the organisation template: `wayscloudas/wayscloud-infra`,
`docs/sonar/README.md`. It is read before anything here is touched. This file records
only what is specific to this repository — how evidence is produced here, and what the
analysis does not see.

| | |
|---|---|
| Sonar project | `wayscloudas_packages` |
| Epic | [#1](https://github.com/wayscloudas/packages/issues/1) (`epic`, `sonar`) |
| Baseline | `live-2026-10-16` (sha256 `3ce97c819b47…`) |
| Open findings | 239 |
| Task issues | one per rule family, linked as sub-issues of the epic |

## Producing evidence while GitHub Actions is down

CI cannot run, so a green `mergeStateStatus` means nothing: the organisation is on the
GitHub Free plan and branch protection is gone. Evidence is produced locally and bound to
the exact head SHA, and **Gitar's review is the gate** — a successful `Gitar` check means
the review ran, not that it approved.

The script lives with the template, in `wayscloudas/wayscloud-infra`:
`docs/sonar/local-check.sh` on branch `ci/local-check` (commit `a067ee5` when this was
written; that branch is still moving, so read it there rather than from a copy). Run it
against this repository from anywhere:

```
<wayscloud-infra>/docs/sonar/local-check.sh "$PWD" --pr <number>
```

It takes the repository path as its first argument, refuses to run unless the working tree
is clean and `HEAD` is the revision it verifies, and prints a block to paste into the pull
request.

### Why the script is not copied into this repository

It was tried, and the copy added **26 new `shelldre:S7688` findings** to this project — the
rule that this campaign has 168 open findings and 11 open tasks for. The script is bash
that uses `[ ]`, which is exactly what `S7688` reports. Neither available answer is
acceptable: a `sonar.issue.ignore.multicriteria` entry for a whole new file would be a
blanket exception (§ 8.1 of the template forbids it), and rewriting the script to use
`[[ ]]` would fork the proof so that the two repositories no longer produce the same
evidence. Running the single upstream copy keeps one source of truth and adds no findings.

A second reason not to fork it: the script was corrected while this change was open
(`077a32c` → `a067ee5`, "the local check could report PASS for tests that never ran"). A
copy would have kept the unsound version and gone on producing green proofs.

## What is checked here

The script finds the checks through the root `pytest.ini` (`testpaths = tests`):

| Check | Command | Covers |
|---|---|---|
| `python: pytest` | `pytest -q` | regression tests for the Python helpers that ship with these packages |

The shell scripts and `Makefile`s are OpenWrt package metadata and install scripts.
Running them needs a buildroot, the target devices, and `micropython`; they are not
executed here. `shellcheck` and `bash -n` read them as text only, which is not the same as
running them, so a finding fixed there is not proven at runtime by this script.

## Blind spots

- The C and C++ sources under `*/src/` are compiled by the OpenWrt build system only.
  Nothing in this repository compiles them, so a change in one is reviewed, not built.
- Coverage is `NOT MEASURED` on this project. The quality gate is green on `new_coverage`
  for the same reason: the condition cannot fail without data. It is not evidence that the
  new code is tested.
- Automatic Analysis sees `shell`, `c`, `cpp`, `githubactions`, `py` and `php` here.
  Anything shipped as an opaque binary or read only by the OpenWrt build is unseen.

## Missing a fix

A finding is closed without a fix only with a written reason that names the consequence,
recorded in [`triage.md`](triage.md). A Sonar finding is never marked as a false positive
in the UI.
